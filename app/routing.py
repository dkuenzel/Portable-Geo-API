from lib.basic_types import *
from lib.requests import *

# Mockup request from config class
from settings.config import config
requestData = config.mockupRequest

# Request

# Origin
originGeocode = geocode(longitude(5.501135), latitude(51.421882))
origin = vertex(geocode=originGeocode)

# Destination
destinationGeocode = geocode(longitude(5.459465), latitude(51.454974))
destination = vertex(geocode=destinationGeocode)

# Routing request
task = route(origin, destination)
# output
for step in task.routingResponse:
	print(step)
print(task.routingDistance)

# Isochrone request
