from api import app
from flask import jsonify
from flask import send_from_directory
from lib.basic_types import *
from lib.requests import *

################### TODO: Outsource db connection to db handler class? Ideally outsource the cursors from the classes as well?
import sys
import psycopg2
import psycopg2.extras
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
# TODO: Implement folder to serve static files from which can be included in html (see /static/favicon folder for html tags)
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(config.static_url_path + '/favicon', 'favicon-32x32.png')
@app.route('/')
def help():
	return send_from_directory(config.static_url_path, 'documentation.html')

## P2P Routing
# Try: http://127.0.0.1:5000/p2p/0/5.125/51.31234/5.12/51.31
@app.route('/p2p/0/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetBeautified(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(pgConnString, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return request.getHtml()
	
# Try: http://127.0.0.1:5000/p2p/1/5.125/51.31234/5.12/51.31
@app.route('/p2p/1/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetRawRoute(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(pgConnString, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getRaw())

## TODO: Implement Output Format 2 (Route only) for routing
# Try: http://127.0.0.1:5000/p2p/2/5.125/51.31234/5.12/51.31
@app.route('/p2p/2/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetRoute(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(pgConnString, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getRoute())

# Try: http://127.0.0.1:5000/p2p/2/5.125/51.31234/5.12/51.31
@app.route('/p2p/3/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetRouteDistance(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(pgConnString, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getDistance())

## Isochrones

## TODO: Implement Output Format 0 (Beautified) for Isochrones

## TODO: Implement Output Format 1 (Raw output) for Isochrones

# Try: http://127.0.0.1:5000/ich/2/5.125/51.31234
@app.route('/ich/2/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetNodes(origin_lon, origin_lat):
	request = Isochrone(pgConnString, config, origin_lon, origin_lat)
	return jsonify(request.getNodes())

# Try: http://127.0.0.1:5000/ich/3/5.125/51.31234
@app.route('/ich/3/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetGeometry(origin_lon, origin_lat):
	request = Isochrone(pgConnString, config, origin_lon, origin_lat)
	return jsonify(request.getGeometry())
