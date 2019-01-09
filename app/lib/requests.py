from lib.basic_types import *
import re


class geoRequest:
	def __init__(self, pgConnString, config, originLon, originLat, dop=0.1, transportationMode=0):
		# Database connection
		self.pgConnString = pgConnString
		self.config = config
		# Origin
		self.origin = Vertex(self.pgConnString, self.config, lon=originLon, lat=originLat)
		# Global modificators
		self.dop = dop # Max distance between input geocode and route network entry vertex
		self.transportationMode = transportationMode  # Used for selection of routing network and moving speed. No further implementation right now, just to be future proof: 0=pedestrian

	# Peer to Peer routing request
	#def p2p(self):
	#	self.result = route(self.pgConnString, self.config, self.origin, self.destination)

	# Isochrone request
	#def ich(self):
	#	self.result = isochrone(self.pgConnString, self.config, self.origin)
	
	# Output Functions
	#def getRaw(self):
	#	return self.result.raw

	# Output Functions
	#def getDistance(self):
	#	return self.result.distance

	#def __str__(self):
	#	output = 'Ways:'
	#	for row in self.result.raw:
	#		output = output + '\n' + str(row)
	#	output = output + '\n' + 'Distance: ' + str(self.getDistance()) + ' Km'
	#	return output

	#def html(self):
	#	output = self.__str__()
	#	output = re.sub(r"\n", "<br>", output)
	#	return output


class Route (geoRequest):
	def __init__(self, pgConnString, config, originLon, originLat, destinationLon, destinationLat, dop=0.01, transportationMode=0):
		super().__init__(pgConnString, config, originLon, originLat, dop, transportationMode)
		# Parameters
		# TODO: Outsource the db conn + cursor creation to an external handler to become more flexible?
		self.dbConn = psycopg2.connect(pgConnString)
		self.dbCursor = self.dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		self.config = config
		self.destination = Vertex(self.pgConnString, self.config, lon=destinationLon, lat=destinationLat)
		# Instance variables
		self.resultsRaw = self._routingRequest()
		self.resultsDistance = self._routingDistance()

	# Output Functions
	def getRaw(self):
		return self.resultsRaw

	# Output Functions
	def getRoute(self):
		route=[]
		for way in self.resultsRaw:
			if way['geom'] is not None:
				route.append(way['geom'])
		return route

	# Output Functions
	def getDistance(self):
		return self.resultsDistance

	def __str__(self):
		output = 'Ways:'
		for row in self.resultsRaw:
			output = output + '\n' + str(row)
		output = output + '\n' + 'Distance: ' + str(self.getDistance()) + ' Km'
		return output

	def getHtml(self):
		output = self.__str__()
		output = re.sub(r"\n", "<br>", output)
		return output

	# Get the data from DB
	def _routingRequest(self):
		# Calculate route
		sql = f"\
			CREATE TEMPORARY TABLE temp_edges ON COMMIT DROP AS ( \
			SELECT id, source, target, cost, reverse_cost, km, geom_way \
				FROM {self.config.edgesTable} \
				WHERE geom_way && ST_Buffer( \
				ST_Envelope(St_MakeLine( \
					ST_SetSRID(ST_MakePoint({self.origin.geocode.longitude.val},{self.origin.geocode.latitude.val}),4326), \
					ST_SetSRID(ST_MakePoint({self.destination.geocode.longitude.val},{self.destination.geocode.latitude.val}),4326))), \
				0.01)); \
				\
				SELECT ds.*, tr.km, ST_AsText(tr.geom_way) as geom \
				FROM pgr_dijkstra \
				('SELECT * FROM temp_edges', {self.origin.vertexId}, {self.destination.vertexId}) AS ds \
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
		for way in self.resultsRaw:
			if way["km"] is not None:
				distance = distance + way["km"]
		return distance


# Calculate Isochrone
class Isochrone (geoRequest):
	def __init__(self, pgConnString, config, originLon, originLat, dop=0.01, transportationMode=0, maxRange=0.45, directed=False,
				 reverseCost=False):
		super().__init__(pgConnString, config, originLon, originLat, dop, transportationMode)
		# DB + Config
		# TODO: Outsource the db conn + cursor creation to an external handler to become more flexible?
		self.dbConn = psycopg2.connect(pgConnString)
		self.dbCursor = self.dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		self.config = config
		# Input Data
		self.maxRange = maxRange
		self.directed = directed
		self.reverseCost = reverseCost
		# Results --> Query on demand to save computation time, ideally fetch nodes and polygon variables in one db operation
		self.resultsNodes = None
		self.resultsGeometry = None

	def getRaw(self):
		if self.resultsNodes is None or self.resultsGeometry is None:
			self.resultsNodes = self.getNodes()
			self.resultsGeometry = self.getGeometry()
		output = {"nodes": self.resultsNodes, "geometry": self.resultsGeometry}
		return output

	def __str__(self):
		if self.resultsNodes is None or self.resultsGeometry is None:
			self.resultsNodes = self.getNodes()
			self.resultsGeometry = self.getGeometry()
		output = 'Nodes:'
		for node in self.resultsNodes:
			output = output + '\n' + str(node)
		output = output + '\n' + 'Geometry:\n'
		output = output + str(self.resultsGeometry)
		return output

	def getHtml(self):
		output = self.__str__()
		output = re.sub(r"\n", "<br>", output)
		return output

	def getNodes(self):
		if self.resultsNodes is None:
			self.resultsNodes = self._queryNodes()
		return self.resultsNodes

	def getGeometry(self):
		if self.resultsGeometry is None:
			self.resultsGeometry = self._queryGeometry()
		return self.resultsGeometry

	def _queryNodes(self):
		sql = f"\
			CREATE TEMPORARY TABLE temp_edges ON COMMIT DROP AS ( \
				SELECT id, source, target, cost, reverse_cost, km \
				FROM {self.config.edgesTable} \
				WHERE geom_way && ST_Buffer( \
					ST_SetSRID(ST_MakePoint({self.origin.geocode.longitude.val},{self.origin.geocode.latitude.val}),4326), \
					0.1 \
				));\
			\
			WITH nodes AS ( \
				SELECT seq, id1 AS node, cost \
				FROM pgr_drivingDistance( \
					'SELECT id, source, target, cost, reverse_cost FROM temp_edges', \
					{self.origin.vertexId}, {self.maxRange}, {self.directed}, {self.reverseCost} \
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
					ST_SetSRID(ST_MakePoint({self.origin.geocode.longitude.val},{self.origin.geocode.latitude.val}),4326), \
					0.1 \
				) \
			);\
			\
			CREATE TEMPORARY TABLE vertex_geometries ON COMMIT DROP AS ( \
				WITH nodes AS ( \
					SELECT seq, id1 AS id, cost \
					FROM pgr_drivingDistance( \
						'SELECT id, source, target, cost, reverse_cost FROM temp_edges', \
						{self.origin.vertexId}, {self.maxRange}, {self.directed}, {self.reverseCost} \
					) \
				) \
				SELECT nodes.id, ST_X(vertices.geom_vertex) AS x, ST_Y(vertices.geom_vertex) AS y \
				FROM nodes LEFT JOIN {self.config.vertexTable} AS vertices ON (nodes.id = vertices.id) \
			); \
			\
			SELECT ST_AsText(pgr_pointsAsPolygon('SELECT id, x, y FROM vertex_geometries'));"
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

	from settings.config import config  # DB Connection: add file which contains standard psycopg2 conn string
	from settings.credentials import pgConnString

	import psycopg2
	import psycopg2.extras

	# class config:
	#	edgesTable = "world_2po_4pgr"
	#	vertexTable = "world_2po_vertex"
	# config=config()

	# from tc_db4_connect_v2 import *
	try:
		dbConn = psycopg2.connect(pgConnString)
		dbCursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	except Exception as e:
		print(f"No connection to DB (reason: {e})")
		sys.exit()

	# Unit tests
	try:
		# Mockup data
		originLon = 5.501135
		originLat = 51.421882
		destinationLon = 5.459465
		destinationLat = 51.454974
		# tests
		print("Testing DB")
		dbCursor.execute(f"SELECT * FROM {config.edgesTable} LIMIT 1;");  # Edges table exists
		print("Testing Routing Class")
		r1 = Route(pgConnString, config, originLon, originLat, destinationLon, destinationLat)
		print(r1)
		print("Testing Isochrone Class")
		i1 = Isochrone(pgConnString, config, originLon, originLat)
		i1.getNodes()
		i1.getGeometry()
		print(i1)

		print("Unit tests for basic_types.py successful")
	except Exception as e:
		print(f"Test failed: {e}")