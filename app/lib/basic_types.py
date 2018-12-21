#!/usr/bin/env python3

"""classes used for i/o and geo operations"""

# Libraries
# TODO: Where do we really need to import those classes and where not?
import psycopg2
import psycopg2.extras


# Classes
class longitude:
	def __init__(self, val):
		self.val = val
		self.validate()
	def validate(self):
		if (self.val > 180) or (self.val < -180):
			return False

class latitude:
	def __init__(self, val):
		self.val = val
		self.validate()
	def validate(self):
		if (self.val > 90) or (self.val < -90):
			return False

class geocode:
	def __init__(self, lon, lat):
		self.longitude = lon
		self.latitude = lat
					
class vertex:
	def __init__(self, pgConnString, config, vertexId=None, geocode=None, dop=None):
		# TODO: Outsource the db conn + cursor creation to an external handler to become more flexible?
		self.dbConn = psycopg2.connect(pgConnString)
		self.dbCursor = self.dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		self.config = config
		self.vertexId = vertexId
		self.geocode = geocode
		self.dop = dop
		
		if self.vertexId is None:
			if self.dop is None:
				self.vertexId = self.getVertexFromGeocode(geocode)
			else:
				self.vertexId = self.getVertexFromGeocode(geocode, self.dop)
				
	
	def getVertexFromGeocode(self, geocode, dop=0.1):
		longitude = geocode.longitude.val 
		latitude = geocode.latitude.val
		
		sql = f"\
				SELECT id \
				FROM {self.config.vertexTable} \
				WHERE st_dwithin(geom_vertex, st_setsrid(st_makepoint({longitude},{latitude}),4326), {dop}) \
				ORDER BY geom_vertex <-> st_setsrid(st_makepoint({longitude},{latitude}),4326) LIMIT 1;"
		self.dbCursor.execute(sql)
		result = self.dbCursor.fetchone()
		
		return (result["id"])

class route:
	def __init__(self, pgConnString, config, originVertex, destinationVertex, dop=0.01, transportationMode = 0):
		# Parameters
		# TODO: Outsource the db conn + cursor creation to an external handler to become more flexible?
		self.dbConn = psycopg2.connect(pgConnString)
		self.dbCursor = self.dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		self.config = config
		self.originVertex = originVertex
		self.destinationVertex = destinationVertex
		self.dop = dop
		self.transportationMode = transportationMode # Used for selection of routing network and moving speed. No further implementation right now, just to be future proof: 0=pedestrian
		# Instance variables
		self.raw = self._routingRequest()
		self.distance = self._routingDistance()
		
	# Get the data from DB
	def _routingRequest(self):
		# Calculate route
		sql = f"\
			CREATE TEMPORARY TABLE temp_edges ON COMMIT DROP AS ( \
			SELECT id, source, target, cost, reverse_cost, km \
				FROM {self.config.edgesTable} \
				WHERE geom_way && ST_Buffer( \
				ST_Envelope(St_MakeLine( \
					ST_SetSRID(ST_MakePoint({self.originVertex.geocode.longitude.val},{self.originVertex.geocode.latitude.val}),4326), \
					ST_SetSRID(ST_MakePoint({self.destinationVertex.geocode.longitude.val},{self.destinationVertex.geocode.latitude.val}),4326))), \
				0.01)); \
				\
				SELECT ds.*, tr.km \
				FROM pgr_dijkstra \
				('SELECT * FROM temp_edges', {self.originVertex.vertexId}, {self.destinationVertex.vertexId}) AS ds \
				LEFT JOIN temp_edges AS tr ON (ds.edge = tr.id) \
				ORDER BY seq;"
		self.dbCursor.execute(sql)
		result = self.dbCursor.fetchall()
		self.dbConn.commit()
		# Return result
		return result
		
	# Calculate route distance
	def _routingDistance(self):
		distance = 0
		for way in self.raw:
			if way["km"] is not None:
				distance = distance + way["km"]
		return distance

# Calculate Isochrone
class isochrone:
	def __init__(self, pgConnString, config, originVertex, dop=0.01, transportationMode=0, maxRange=10, directed=False, reverseCost=False):
		# DB + Config
		# TODO: Outsource the db conn + cursor creation to an external handler to become more flexible?
		self.dbConn = psycopg2.connect(pgConnString)
		self.dbCursor = self.dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		self.config = config
		# Input Data
		self.originVertex = originVertex
		self.dop = dop
		self.transportationMode = transportationMode
		self.maxRange = maxRange
		self.directed = directed
		self.reverseCost = reverseCost
		# Results --> Query on demand to save computation time, ideally fetch nodes and polygon variables in one db operation
		self.nodes = None
		self.geometry = None

	def getNodes(self):
		if self.nodes is None:
			self.nodes = self._queryNodes()
		return self.nodes

	def getGeometry(self):
		if self.geometry is None:
			self.geometry = self._queryGeometry()
		return self.geometry

	def _queryNodes(self):
		sql = f"\
			CREATE TEMPORARY TABLE temp_edges ON COMMIT DROP AS ( \
				SELECT id, source, target, cost, reverse_cost, km \
				FROM {self.config.edgesTable} \
				WHERE geom_way && ST_Buffer( \
					ST_SetSRID(ST_MakePoint({self.originVertex.geocode.longitude.val},{self.originVertex.geocode.latitude.val}),4326), \
					0.1 \
				));\
			\
			WITH nodes AS ( \
				SELECT seq, id1 AS node, cost \
				FROM pgr_drivingDistance( \
					'SELECT id, source, target, cost, reverse_cost FROM temp_edges', \
					{self.originVertex.vertexId}, {self.maxRange}, {self.directed}, {self.reverseCost} \
				) \
			) \
			\
			SELECT * \
			FROM nodes;"
		self.dbCursor.execute(sql)
		result = self.dbCursor.fetchall()
		self.dbConn.commit()
		# Return result
		return result

	def _queryGeometry(self):
		sql = f"\
			CREATE TEMPORARY TABLE temp_edges ON COMMIT DROP AS ( \
				SELECT id, source, target, cost, reverse_cost, km \
				FROM {self.config.edgesTable} \
				WHERE geom_way && ST_Buffer( \
					ST_SetSRID(ST_MakePoint({self.originVertex.geocode.longitude.val},{self.originVertex.geocode.latitude.val}),4326), \
					0.1 \
				) \
			);\
			\
			CREATE TEMPORARY TABLE vertex_geometries ON COMMIT DROP AS ( \
				WITH nodes AS ( \
					SELECT seq, id1 AS id, cost \
					FROM pgr_drivingDistance( \
						'SELECT id, source, target, cost, reverse_cost FROM temp_edges', \
						{self.originVertex.vertexId}, {self.maxRange}, {self.directed}, {self.reverseCost} \
					) \
				) \
				SELECT nodes.id, ST_X(vertices.geom_vertex) AS x, ST_Y(vertices.geom_vertex) AS y \
				FROM nodes LEFT JOIN {self.config.vertexTable} AS vertices ON (nodes.id = vertices.id) \
			); \
			\
			SELECT pgr_pointsAsPolygon('SELECT id, x, y FROM vertex_geometries');"
		self.dbCursor.execute(sql)
		result = self.dbCursor.fetchall()
		self.dbConn.commit()
		# Return result
		return result

if (__name__ == "__main__"):	
	## Testing
	# Libraries
	import sys
	sys.path.append('..')
	
	from settings.config import config # DB Connection: add file which contains standard psycopg2 conn string
	from settings.credentials import pgConnString
	
	import psycopg2
	import psycopg2.extras
	
	#class config:
	#	edgesTable = "world_2po_4pgr"
	#	vertexTable = "world_2po_vertex"
	#config=config()

	#from tc_db4_connect_v2 import *
	try:
		dbConn = psycopg2.connect(pgConnString)
		dbCursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	except Exception as e:
		print (f"No connection to DB (reason: {e})")
		sys.exit()
		
	# Unit tests
	try:
		print("Testing DB")
		dbCursor.execute(f"SELECT * FROM {config.edgesTable} LIMIT 1;"); # Edges table exists
		print("Testing Longitude Class")
		x1 = longitude(5.501135) # Test Longitude Class
		x2 = longitude(5.459465) # Test Longitude Class
		print(x1)
		print("Testing Latitude Class")
		y1 = latitude(51.421882) # Test Latitude Class
		y2 = latitude(51.454974) # Test Latitude Class
		print(y1)
		print("Testing Geocode Class")
		g1 = geocode(x1,y1)
		g2 = geocode(x2,y2)
		print(g1)
		print("Testing Vertex Class")
		v1=vertex(pgConnString, config, geocode=g1) # Test vertex class
		v2=vertex(pgConnString, config, geocode=g2) # Test vertex class
		print(v1)
		print("Testing Routing Class")
		r1=route(pgConnString, config, v1, v2)
		print(r1)
		print("Testing Isochrone Class")
		i1=isochrone(pgConnString, config, v1)
		i1.getNodes()
		i1.getGeometry()
		print(i1)

		print("Unit tests for basic_types.py successful")
	except Exception as e:
		print(f"Test failed: {e}")
