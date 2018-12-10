#!/usr/bin/env python3

"""gets closest osm vertex from db"""

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
		if (self.val > 180) or (self.val < -180):
			return False

class geocode:
	def __init__(self, lon, lat):
		self.longitude = lon
		self.latitude = lat
					
class vertex:
	def __init__(self, vertexId=None, geocode=None):
		self.dop = None
		self.vertexId = vertexId
		self.geocode = geocode
		
		if self.vertexId is None:
			self.vertexId = self.getVertexFromGeocode(geocode)
	
	def getVertexFromGeocode(self, geocode, dop=0.1):
		longitude = geocode.longitude.val 
		latitude = geocode.latitude.val
		
		sql = f"\
				SELECT * \
				FROM {config.vertexTable} \
				WHERE st_dwithin(geom_vertex, st_setsrid(st_makepoint({longitude},{latitude}),4326), {dop}) \
				ORDER BY geom_vertex <-> st_setsrid(st_makepoint({longitude},{latitude}),4326) LIMIT 1;"
		dbCursor.execute(sql)
		result = dbCursor.fetchone()
		
		return (result["id"])

class routingRequest:
	def __init__(self, originVertex, destinationVertex, dop=0.01):
		self.origin = originVertex
		self.destination = destinationVertex
		self.dop = dop
		self.route = self.calculateRoute()
	
	def calculateRoute(self):
		# Calculate route
		sql = f"\
			CREATE TEMPORARY TABLE temp_routing_edges ON COMMIT DROP AS ( \
			SELECT * \
				FROM {config.edgesTable} \
				WHERE geom_way && ST_Buffer( \
				ST_Envelope(St_MakeLine( \
					ST_SetSRID(ST_MakePoint({self.origin.geocode.longitude.val},{self.origin.geocode.latitude.val}),4326), \
					ST_SetSRID(ST_MakePoint({self.destination.geocode.longitude.val},{self.destination.geocode.latitude.val}),4326))), \
				0.01)); \
				\
				SELECT * \
				FROM pgr_dijkstra \
				('SELECT * FROM temp_routing_edges', {self.origin.vertexId}, {self.destination.vertexId});"
		dbCursor.execute(sql)
		result = dbCursor.fetchall()
		dbConn.commit()
		# Return result
		return result


if (__name__ == "__main__"):	
	## Testing
	# Libraries
	import sys
	import psycopg2
	import psycopg2.extras
	
	class config:
		edgesTable = "world_2po_4pgr"
		vertexTable = "world_2po_vertex"
	config=config()

	# DB Connection# DB connection
	sys.path.append('/home/dkuenzel/credentials')
	from aladin_testa_osm_routing import *
	#from tc_db4_connect_v2 import *
	try:
		dbConn = psycopg2.connect(conn_string)
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
		v1=vertex(geocode=g1) # Test vertex class
		v2=vertex(geocode=g2) # Test vertex class
		print(v1)
		print("Testing Routing Class")
		r1=routingRequest(v1, v2)
		print(r1)
		print("Unit tests for classes.py successful")
	except Exception as e:
		print(f"Test failed: {e}")
