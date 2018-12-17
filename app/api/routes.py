from api import app
from flask import jsonify
from lib.basic_types import *
from lib.requests import *

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
def getRawRouteBeautified(origin_lon, origin_lat, destination_lon, destination_lat):
	request = geoRequest(origin_lon, origin_lat, destination_lon, destination_lat)
	request.p2p()
	return request.html()
	
# Try: http://127.0.0.1:5000/p2p/1/5.125/51.31234/5.12/51.31
@app.route('/p2p/1/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def getRawRoute(origin_lon, origin_lat, destination_lon, destination_lat):
	request = geoRequest(origin_lon, origin_lat, destination_lon, destination_lat)
	request.p2p()
	return jsonify(request.getRaw())
