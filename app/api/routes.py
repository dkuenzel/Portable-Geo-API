from api import app
from flask import jsonify
from flask import send_from_directory
from lib.basic_types import *
from lib.requests import *

################### TODO: Outsource db connection to db handler class? Ideally outsource the cursors from the classes as well?
import os
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


## Routes for static content
#config.static_url_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
#print (config.static_url_path)
@app.route('/static/vendor/<string:filename>', methods=['GET'])
def getVendorLib(filename):
	return send_from_directory(config.static_url_path + '/vendor', filename)
@app.route('/static/maps/<string:filename>', methods=['GET'])
def getMapImage(filename):
	return send_from_directory(config.static_url_path + '/map-images', filename)
# Workaround TODO: Place proper tags in html and link to favicon folder instead
@app.route('/static/favicon/<string:filename>', methods=['GET'])
def getFavicon(filename):
	return send_from_directory(config.static_url_path + '/favicon', filename)


## Dynamic Routes
# Output documentation with sandbox for requests on root

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

# Try: http://127.0.0.1:5000/p2p/2/5.125/51.31234/5.12/51.31
@app.route('/p2p/2/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetRouteDistance(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(pgConnString, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getDistance())

# Try: http://127.0.0.1:5000/p2p/3/5.125/51.31234/5.12/51.31
@app.route('/p2p/3/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetRoute(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(pgConnString, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getRoute())


## Isochrones
# Try: http://127.0.0.1:5000/ich/0/0.25/5.125/51.31234
@app.route('/ich/0/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetBeautified(max_range, origin_lon, origin_lat):
	request = Isochrone(pgConnString, config, origin_lon, origin_lat, maxRange=max_range)
	return request.getHtml()

# Try: http://127.0.0.1:5000/ich/1/0.25/5.125/51.31234
@app.route('/ich/1/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetRaw(max_range, origin_lon, origin_lat):
	request = Isochrone(pgConnString, config, origin_lon, origin_lat, maxRange=max_range)
	return jsonify(request.getRaw())

# Try: http://127.0.0.1:5000/ich/2/0.25/5.125/51.31234
@app.route('/ich/2/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetNodes(max_range, origin_lon, origin_lat):
	request = Isochrone(pgConnString, config, origin_lon, origin_lat, maxRange=max_range)
	return jsonify(request.getNodes())

# Try: http://127.0.0.1:5000/ich/0.25/3/5.125/51.31234
@app.route('/ich/3/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetGeometry(max_range, origin_lon, origin_lat):
	request = Isochrone(pgConnString, config, origin_lon, origin_lat, maxRange=max_range)
	return jsonify(request.getGeometry())
