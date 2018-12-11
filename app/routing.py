
# Libraries
import sys
import psycopg2
import psycopg2.extras

from config import *

from lib.classes import *
from lib.functions import *


# Mockup request from config class
requestData = config.mockupRequest

# DB Connection
db_params = "dbname=test user=testa password=wa08ef328jfßpij"
try:
	dbConn = psycopg2.connect(db_params)
	dbCursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
except Exception as e:
	print (f"No connection to DB (reason: {e})")
	sys.exit()

# Request
origin = vertex(5.501135, 51.421882)
destination = vertex(5.459465, 51.454974)
task = routingRequest(origin, destination)

# output
print(task)
