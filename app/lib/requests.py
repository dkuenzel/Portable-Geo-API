from lib.basic_types import *

class geoRequest:
	def __init__(self, origin_lon, origin_lat, destination_lon, destination_lat):
		# Origin
		originGeocode = geocode(longitude(origin_lon), latitude(origin_lat))
		self.origin = vertex(geocode=originGeocode)
		# Destination
		destinationGeocode = geocode(longitude(destination_lon), latitude(destination_lat))
		self.destination = vertex(geocode=destinationGeocode)

	# Peer to Peer routing request
	def p2p(self):
		task = route(self.origin, self.destination)
		# output
		for step in task.routingResponse:
			print(step)
		print(task.routingDistance)
