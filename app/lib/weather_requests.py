from lib.basic_types import *
import re

class DbHandler:
	def __init__(self, pgConnString):
		self.result = None
		self.pgConnString = pgConnString
		self.dbConn = psycopg2.connect(self.pgConnString)
		self.dbCursor = self.dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	
	worldclimate = { \
	"tmin": "worldclimate_v2_tmin", \
	"tmax": "worldclimate_v2_tmax", \
	"tavg": "worldclimate_v2_tavg", \
	"prec": "worldclimate_v2_prec", \
	"srad": "worldclimate_v2_srad", \
	"wind": "worldclimate_v2_wind", \
	"vapr": "worldclimate_v2_vapr", \
	"biovars": "worldclimate_v2_biovars"}

	def queryRaw(self, querystring):
		self.dbCursor.execute(querystring)
		self.result = self.dbCursor.fetchall()
		self.dbConn.commit()
	

		

class weatherRequest:
	def __init__(self, config, longitude, latitude, referenceId = None):
		self.referenceId = referenceId
		# Database connection
		# TODO: Outsource the db conn + cursor creation to an external handler to become more flexible (cave: closed connection errors)
		self.dbHandler = DbHandler()
		# location
		self.longitude = Longitude(longitude)
		self.latitude = Latitude(latitude)
		#Get Data
		self.rawData = queryAll()
		self.data = {}
	
	def _GetAttributeFromDb(self, attribute):
			sql = f"SELECT * FROM (SELECT {self.referenceId} AS reference, {self.longitude}}::NUMERIC AS x, {self.latitude}::NUMERIC AS y) AS destinations, LATERAL (SELECT * FROM {AttributeDbFunction}(destinations.x, destinations.y, {self.referenceId}::INTEGER) AS $attribute) sub;";

	def queryAll(self):
		self.getTmax
		

	def getTmax(self):
		self.data.tmax = self.dbHandler("")	
	
	# Output Functions
	def getRaw(self):
		self.queryAll()
		return self.rawData
		
	def getHtml(self):
		pass

	def getGeometry(self):
		pass