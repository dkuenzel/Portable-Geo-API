# Mockup request
requestData = {"origin": {"lon": 5.23487, "lat": 52.123412}, "destination": {"lon": 5.23487, "lat": 52.623412}, "dop": 0.01}


# Libraries
import sys
import psycopg2
import psycopg2.extras

from scripts.classes import *
from scripts.functions import *

from config import *

# DB Connection
db_params = "dbname=test user=testa password=wa08ef328jfßpij"
try:
	dbConn = psycopg2.connect(db_params)
	dbCursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
except Exception as e:
	print (f"No connection to DB (reason: {e})")
	sys.exit()

# Request
origin = vertex(5.2348172, 52.32465)
destination = vertex(5.2348172, 51.32465)
task = routingRequest(origin, destination)

# output
print(task)
