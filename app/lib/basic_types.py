#!/usr/bin/env python3

"""classes used for i/o and geo operations"""

# Libraries
# TODO: Where do we really need to import those classes and where not?
import psycopg2
import psycopg2.extras


# Classes
class Longitude:
	def __init__(self, val):
		self.val = val
		self.validate()
	def validate(self):
		if (self.val is None):
			return False
		if (self.val > 180) or (self.val < -180):
			return False

class Latitude:
	def __init__(self, val):
		self.val = val
		self.validate()
	def validate(self):
		if (self.val is None):
			return False
		if (self.val > 90) or (self.val < -90):
			return False

class Geocode:
	def __init__(self, lon, lat):
		self.longitude = lon
		self.latitude = lat
					
class Vertex:
	def __init__(self, pgConnString, config, vertexId=None, geocode=None, lon=None, lat=None, dop=0.1):
		# TODO: Outsource the db conn + cursor creation to an external handler to become more flexible?
		self.dbConn = psycopg2.connect(pgConnString)
		self.dbCursor = self.dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		self.config = config
		self.vertexId = vertexId
		self.geocode = geocode
		self.dop = dop

		if self.geocode is not None:
			self.vertexId = self.getVertexFromGeocode()
		elif (lon is not None) & (lat is not None):
			self.geocode = Geocode(Longitude(lon), Latitude(lat))
			self.vertexId = self.getVertexFromGeocode()
		elif self.vertexId is not None:
			print('Initializing a vertex by its id is not yet implemented!') ## TODO: Implement initialization of vertex objects by vertexId
		else:
			print('Incomplete input data for vertex object initialization!')
	
	def getVertexFromGeocode(self):
		longitude = self.geocode.longitude.val
		latitude = self.geocode.latitude.val
		return self.getVertexFromLonLat(longitude, latitude)

	def getVertexFromLonLat(self, longitude, latitude):
		sql = f"\
				SELECT id \
				FROM {self.config.vertexTable} \
				WHERE st_dwithin(geom_vertex, st_setsrid(st_makepoint({longitude},{latitude}),4326), {self.dop}) \
				ORDER BY geom_vertex <-> st_setsrid(st_makepoint({longitude},{latitude}),4326) LIMIT 1;"
		self.dbCursor.execute(sql)
		result = self.dbCursor.fetchone()
		return (result["id"])


if (__name__ == "__main__"):	
	## Testing
	# Libraries

	#import traceback

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
		lon = 5.501135
		lat = 51.421882
		print("Testing DB")
		dbCursor.execute(f"SELECT * FROM {config.edgesTable} LIMIT 1;") # Edges table exists
		print("Testing Longitude Class")
		x1 = Longitude(lon) # Test Longitude Class
		print(x1)
		print(x1.val)
		print("Testing Latitude Class")
		y1 = Latitude(lat) # Test Latitude Class
		print(y1)
		print(y1.val)
		print("Testing Geocode Class")
		g1 = Geocode(x1,y1)
		print(g1)
		print(g1.longitude.val)
		print(g1.latitude.val)
		print("Testing Vertex Class")
		v1=Vertex(pgConnString, config, geocode=g1) # Test vertex class initialization by geocode
		print(v1)
		print(v1.vertexId)
		print(v1.geocode.longitude.val)
		print(v1.geocode.latitude.val)
		v2=Vertex(pgConnString, config, lon=lon, lat=lat) # Test vertex class initialization by lon/lat
		print(v2)

		print("Unit tests for basic_types.py successful")
	except Exception as e:
		print(f"Test failed: {e}")
		#print(traceback.print_stack())
		#print(repr(traceback.extract_stack()))
		#print(repr(traceback.format_stack()))
