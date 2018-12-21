###################
import sys
import psycopg2
import psycopg2.extras
#sys.path.append('..')
from settings.config import config
from settings.credentials import pgConnString # DB Connection: add file which contains standard psycopg2 conn string
# DB Connection
try:
	dbConn = psycopg2.connect(pgConnString)
	dbCursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
except Exception as e:
	print (f"No connection to DB (reason: {e})")
	sys.exit()
###################

# Mockup request
origin_lon = 5.501135
origin_lat = 51.421882
destination_lon = 5.459465
destination_lat = 51.454974

# Inherit request class and get results
from lib.basic_types import *
from lib.requests import *
request = geoRequest(dbConn, config, origin_lon, origin_lat, destination_lon, destination_lat)
request.p2p()
print(request)

# TODO: Isochrone request
# TODO: 1:n
# TODO: n:n

# API
from api import app

