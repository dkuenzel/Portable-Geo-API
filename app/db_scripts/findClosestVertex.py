#!/usr/bin/env python3

"""gets closest osm vertex from db"""

class vertex:
	def __init__(self):
		self.dop = None
		self.sourceId = None
		
		if (checkCoordinates()):
			self.sourceId = getVertexForLonLat()

class route:
	def __init__(self):
		self.v1=None
		self.v2=None
		self.route=None

def getVertexFromLonLat(latitude=None, longitude=None, dop=0.1):
	if (checkCoordinates(longitude, latitude)) is False:
		return False
		
	sql = f"\
		BEGIN; \
			CREATE TEMPORARY TABLE edges AS ( \
			SELECT * \
			FROM {config.edgesTable} \
			WHERE geom_way && ST_Buffer( \
			ST_Envelope(St_MakeLine( \
				ST_SetSRID(ST_MakePoint({longitude},{latitude}),4326), \
				ST_SetSRID(ST_MakePoint({longitude},{latitude}),4326))), \
			0.01)); \
			\
			SELECT * \
			FROM edges \
			WHERE st_dwithin(geom_vertex, st_setsrid(st_makepoint({longitude},{latitude}),4326), {dop}) \
			ORDER BY geom_vertex <-> st_setsrid(st_makepoint({longitude},{latitude}),4326) LIMIT 1; \
		END;"
	vertex = pq_query()
		

def checkCoordinates(longitude, latitude):
	if (longitude > 180) or (longitude < -180):
		return False
	if (latitude > 90) or (latitude < -90):
		return False

if (__name__ == "__main__"):
	# Libraries
	import sys
	import psycopg2
	import psycopg2.extras

	# DB Connection
	db_params = "dbname=test user=testa password=wa08ef328jfßpij"
	try:
		dbConn = psycopg2.connect(db_params)
		dbCursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	except Exception as e:
		print (f"No connection to DB (reason: {e})")
		sys.exit()
	
	# Test
	try:
		dbCursor.query(f"SELECT COUNT (*) FROM {edgesTable} LIMIT 1;"); # Edges table exists
		tv1=vertex(5.234234,52.1234123) # Test vertex class
		tv2=vertex(5.234234,51.1234123) # Test vertex class
		r1=route(tv1, tv2) # Test route class
		print(r1)
	except Exception as e:
		print(f"Test failed: {e}" )
