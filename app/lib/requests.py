from lib.basic_types import *
import re

class geoRequest:
	def __init__(self, db, config, origin_lon, origin_lat, destination_lon, destination_lat):
		# Database connection
		self.db = db
		self.config = config
		# Origin
		self.originGeocode = geocode(longitude(origin_lon), latitude(origin_lat))
		self.origin = vertex(self.db, self.config, geocode=self.originGeocode)
		# Destination
		self.destinationGeocode = geocode(longitude(destination_lon), latitude(destination_lat))
		self.destination = vertex(self.db, self.config, geocode=self.destinationGeocode)
		# Class vars
		self.result = None

	# Peer to Peer routing request
	def p2p(self):
		self.result = route(self.db, self.config, self.origin, self.destination)
	
	# Output Functions
	def getRaw(self):
		return self.result.raw

	# Output Functions
	def getDistance(self):
		return self.result.distance
	
	def __str__(self):
		output = 'Ways:'
		for row in self.result.raw:
			output = output + '\n' + str(row)
		output = output + '\n' + 'Distance: ' + str(self.getDistance()) + ' Km'
		return output
	
	def html(self):
		output = self.__str__()
		output = re.sub(r"\n", "<br>", output)
		return output
