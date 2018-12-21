from api import app
from flask import jsonify
from lib.basic_types import *
from lib.requests import *

################### Outsource
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

## Allow negative values in request
from werkzeug.routing import FloatConverter as BaseFloatConverter
class FloatConverter(BaseFloatConverter):
    regex = r'-?\d+(\.\d+)?'
app.url_map.converters['float'] = FloatConverter

## Routes
# Output help for requests on root
@app.route('/')
def help():
	text = '<br>\
	Format for peer 2 peer requests: "/p2p/integer:output/float:origin_lon/float:origin_lat/float:destination_lon/float:destination_lat<br>"\
	Where:<br>\
	output = <br>\
		0) Beautified<br>\
		1) Raw output<br>\
		2) Route only<br>\
		3) Distance only'
	return text

# Try: http://127.0.0.1:5000/p2p/0/5.125/51.31234/5.12/51.31
@app.route('/p2p/0/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def getBeautified(origin_lon, origin_lat, destination_lon, destination_lat):
	request = geoRequest(dbConn, config, origin_lon, origin_lat, destination_lon, destination_lat)
	request.p2p()
	return request.html()
	
# Try: http://127.0.0.1:5000/p2p/1/5.125/51.31234/5.12/51.31
@app.route('/p2p/1/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def getRawRoute(origin_lon, origin_lat, destination_lon, destination_lat):
	request = geoRequest(dbConn, config, origin_lon, origin_lat, destination_lon, destination_lat)
	request.p2p()
	return jsonify(request.getRaw())
	
# Try: http://127.0.0.1:5000/p2p/2/5.125/51.31234/5.12/51.31
@app.route('/p2p/2/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def getRouteDistance(origin_lon, origin_lat, destination_lon, destination_lat):
	request = geoRequest(dbConn, config, origin_lon, origin_lat, destination_lon, destination_lat)
	request.p2p()
	return jsonify(request.getDistance())
