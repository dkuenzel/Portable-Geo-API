from lib.basic_types import *
from lib.requests import *

# Mockup request
# Origin
origin_lon = 5.501135
origin_lat = 51.421882
originGeocode = geocode(longitude(origin_lon), latitude(origin_lat))
originVertex = vertex(geocode=originGeocode)

# Destination
destination_lon = 5.459465
destination_lat = 51.454974
destinationGeocode = geocode(longitude(destination_lon), latitude(destination_lat))
destinationVertex = vertex(geocode=destinationGeocode)

# Direct routing request
task = route(originVertex, destinationVertex)
# output
for step in task.routingResponse:
	print(step)
print(task.routingDistance)

# Inherit request class
request = geoRequest(origin_lon, origin_lat, destination_lon, destination_lat)

# Isochrone request
