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
from settings.credentials import DbCredentials # DB Connection: class which contains standard psycopg2 conn strings
## Connection to routing database
try:
	dbConnRouting = psycopg2.connect(DbCredentials.routing)
	dbCursorRouting = dbConnRouting.cursor(cursor_factory=psycopg2.extras.DictCursor)
except Exception as e:
	print (f"No connection to routing DB (reason: {e})")
	sys.exit()
## Connection to weather database
try:
	dbConnWeather = psycopg2.connect(DbCredentials.weather)
	dbCursorWeather = dbConnWeather.cursor(cursor_factory=psycopg2.extras.DictCursor)
except Exception as e:
	print (f"No connection to weather DB (reason: {e})")
	sys.exit()
###################

## Allow negative values in request
from werkzeug.routing import FloatConverter as BaseFloatConverter
class FloatConverter(BaseFloatConverter):
	regex = r'-?\d+(\.\d+)?'
app.url_map.converters['float'] = FloatConverter


## Dynamic Routes
	
#config.static_url_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
#print (config.static_url_path)
## TODO: Implement generic route definition which catches recursively all folders and files in /static
## TODO: Check if input validation/sanitation is needed here
## Static Content
@app.route('/static/<string:topDir>/<string:subDir>/<string:fileName>', methods=['GET'])
def getStaticContent(topDir, subDir, fileName):
	return send_from_directory(config.static_url_path + f"/{topDir}" + f"/{subDir}", fileName)
## Static Content in subdirs 
@app.route('/static/<string:topDir>/<string:subDir>/<string:subSubDir>/<string:fileName>', methods=['GET'])
def getStaticContentFromSubDir(topDir, subDir, subSubDir, fileName):
	return send_from_directory(config.static_url_path + f"/{topDir}" + f"/{subDir}" + f"/{subSubDir}", fileName)


## Static Routes

## Output documentation with sandbox for requests on root
@app.route('/')
def help():
	return send_from_directory(config.static_url_path + '/documentation', 'index.html')

## Request Routes
## TODO: Implement option to select if public transport lines should be included

## P2P Routing
# Try: http://127.0.0.1:5000/p2p/0/5.125/51.31234/5.12/51.31
@app.route('/p2p/0/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetBeautified(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(DbCredentials.routing, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return request.getHtml()
	
# Try: http://127.0.0.1:5000/p2p/1/5.125/51.31234/5.12/51.31
@app.route('/p2p/1/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetRawRoute(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(DbCredentials.routing, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getRaw())

# Try: http://127.0.0.1:5000/p2p/2/5.125/51.31234/5.12/51.31
@app.route('/p2p/2/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetRouteDistance(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(DbCredentials.routing, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getDistance())

# Try: http://127.0.0.1:5000/p2p/3/5.125/51.31234/5.12/51.31
@app.route('/p2p/3/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetGeometry(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(DbCredentials.routing, config, origin_lon, origin_lat, destination_lon, destination_lat)
	return jsonify(request.getGeometry())

# TODO: Implement optimization for line geometries if necessary. So far the singleGeometry parameter is ignored, instead the standard version of the geometry is delivered. 
# This route only exists to provide an entry point for p2p with function 4 (==optimized gemetry) to prevent fiddling with the frontend!!
# Try: http://127.0.0.1:5000/p2p/4/5.125/51.31234/5.12/51.31
@app.route('/p2p/4/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def p2pGetSingleGeometry(origin_lon, origin_lat, destination_lon, destination_lat):
	request = Route(DbCredentials.routing, config, origin_lon, origin_lat, destination_lon, destination_lat, singleGeometry=True)
	return jsonify(request.getGeometry())


## Isochrones
# Try: http://127.0.0.1:5000/ich/0/0.25/5.125/51.31234
@app.route('/ich/0/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetBeautified(max_range, origin_lon, origin_lat):
	request = Isochrone(DbCredentials.routing, config, origin_lon, origin_lat, maxRange=max_range)
	return request.getHtml()

# Try: http://127.0.0.1:5000/ich/1/0.25/5.125/51.31234
@app.route('/ich/1/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetRaw(max_range, origin_lon, origin_lat):
	request = Isochrone(DbCredentials.routing, config, origin_lon, origin_lat, maxRange=max_range)
	return jsonify(request.getRaw())

# Try: http://127.0.0.1:5000/ich/2/0.25/5.125/51.31234
@app.route('/ich/2/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetNodes(max_range, origin_lon, origin_lat):
	request = Isochrone(DbCredentials.routing, config, origin_lon, origin_lat, maxRange=max_range)
	return jsonify(request.getNodes())

# Try: http://127.0.0.1:5000/ich/0.25/3/5.125/51.31234
@app.route('/ich/3/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetGeometry(max_range, origin_lon, origin_lat):
	request = Isochrone(DbCredentials.routing, config, origin_lon, origin_lat, maxRange=max_range)
	return jsonify(request.getGeometry())

# Try: http://127.0.0.1:5000/ich/0.25/4/5.125/51.31234
@app.route('/ich/4/<float:max_range>/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def ichGetAlphaOptimizedGeometry(max_range, origin_lon, origin_lat):
	request = Isochrone(DbCredentials.routing, config, origin_lon, origin_lat, maxRange=max_range, alphaValue=0.00001)
	return jsonify(request.getGeometry())


# TODO: Implement routes to all functions of the weather API
## Weather
# Try: http://127.0.0.1:5000/wea/tmax/5.125/51.31234
@app.route('/wea/tmax/<float:origin_lon>/<float:origin_lat>', methods=['GET'])
def weaTmx(origin_lon, origin_lat):
	request = Weather(DbCredentials.weather, config, origin_lon, origin_lat, maxRange=max_range)
	return request.getTmax()