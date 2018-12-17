from lib.basic_types import *
from lib.requests import *

# Mockup request
origin_lon = 5.501135
origin_lat = 51.421882
destination_lon = 5.459465
destination_lat = 51.454974

# Inherit request class and get results
request = geoRequest(origin_lon, origin_lat, destination_lon, destination_lat)
request.p2p()
print(request)

# TODO: Isochrone request
# TODO: 1:n
# TODO: n:n
