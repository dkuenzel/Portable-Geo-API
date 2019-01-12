// Globals
var baseUrl = window.location.origin  // Get base API URL
var mapFeatureDict = {}  // Container for the map mapFeatureDict 
startCenter=[51.21358759080191, 6.7471182346344]

// Functions
function zoomToFeatures(){

}

function removeMultiFeature(featureArray){
	for (i in featureArray){
		map.removeLayer(featureArray[i]);
	}
}

// Icons
var PedestrianIconClass = L.Icon.extend({
	options: {
		iconUrl: '/static/images/icons/icon-walk.png',
		iconSize:	  [20, 30],
		iconAnchor:	[10, 15],
		popupAnchor:  [7, -15]
	}
});

// Map instance
var map = L.map('map-div').setView(startCenter, 15);

pedestrianIcon = new PedestrianIconClass();

// Base Map
// OSM Style map
baseMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	minZoom: 3,
	noWrap:true,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

// Simplistic global Style map
/*
baseMap = L.tileLayer.wms('https://demo.boundlessgeo.com/geoserver/ows?', {
	layers: 'ne:ne'
});
*/

// Mapbox Style map
//ACCESS_TOKEN = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw';
//baseMap = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' + ACCESS_TOKEN, {
//	maxZoom: 18,
//	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
//		'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
//		'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
//	id: 'mapbox.streets'
//});

baseMap.addTo(map);

// Browser coordinates
var x = document.getElementById("notification-area");
function getLocation() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(showPosition);
	} else {
		x.innerHTML = "Geolocation is not supported by this browser.";
	}
}

function showPosition(position) {
	browserGeocode = {"longitude": position.coords.longitude, "latitude": position.coords.latitude}
	addBrowserLocationAsOrigin(browserGeocode)
}

function addBrowserLocationAsOrigin (browserGeocode) {
	longitude = browserGeocode.longitude
	latitude = browserGeocode.latitude
	$("#origin-longitude-field").val(longitude)
	$("#origin-latitude-field").val(latitude)
	map.flyTo([latitude, longitude], 13)
	if (mapFeatureDict["result"]) {removeMultiFeature(mapFeatureDict["result"])};
	if (mapFeatureDict["origin"]) { map.removeLayer(mapFeatureDict["origin"]); }
	if (mapFeatureDict["browser"]) { map.removeLayer(mapFeatureDict["browser"]); }
	mapFeatureDict["browser"] = L.marker([latitude, longitude], {icon: pedestrianIcon})
	mapFeatureDict["browser"].addTo(map).bindPopup('Your Browser Location (I know, the NSA could do better...)').openPopup();
}

// Coordinates from map
var field = ""
function getCoordsFromMap (e) {
	coord = e.latlng;
	var latitude = coord.lat;
	var longitude = coord.lng;
	$("#" + field + "-longitude-field").val(longitude)
	$("#" + field + "-latitude-field").val(latitude)
	if (mapFeatureDict["result"]){removeMultiFeature(mapFeatureDict["result"])};
	if (mapFeatureDict[field]) { map.removeLayer(mapFeatureDict[field]); }
	mapFeatureDict[field] = L.marker([latitude, longitude], {icon: pedestrianIcon})
	mapFeatureDict[field].addTo(map).bindPopup('Your ' + field + ' location').openPopup();
	deactivateCoordsFromMap();
}
function activateCoordsFromMap (e) {
	field = e
	map.on('click', function(e){ getCoordsFromMap(e) });
}
function deactivateCoordsFromMap () { 
	map.off('click', function(e){ getCoordsFromMap(e) });
}

// Build request from input fields
function buildRequest() {
	apiFunction = $("#api-function-select").val()
	if (apiFunction == "p2p") {
		requestString = $("#base-url").val() + "/" + $("#api-function-select").val() + "/" + $("#output-format-select").val() + "/" + $("#origin-longitude-field").val() + "/" + $("#origin-latitude-field").val() + "/" + $("#destination-longitude-field").val() + "/" + $("#destination-latitude-field").val()
	}
	if (apiFunction == "ich") {
		requestString = $("#base-url").val() + "/" + $("#api-function-select").val() + "/" + $("#output-format-select").val() + "/" + $("#range-field").val() + "/" + $("#origin-longitude-field").val() + "/" + $("#origin-latitude-field").val()
	}
	if ($("#notification-area").text() == ""){
		$("#notification-area").parent().prev('.ss_button').click();
	}
	$("#notification-area").text("Request String: " + requestString)
	
	return requestString
}

// Ajax request
function sendRequest() {
	request = buildRequest()
	if ($("#result-area").text() == ""){
		$("#result-area").parent().prev('.ss_button').click();
	}
	$("#result-area").text("loading data...");
	$.ajax({
		url: request,
		cache: false
	})
		.done(function(result) {
			if ($("#output-format-select").val() == 0) {
				$("#result-area").html(result)
			}  // Beautified output
			if ($("#output-format-select").val() == 1 || $("#output-format-select").val() == 2) {  // JSON output
				result = JSON.stringify(result, null, '\t');
				$("#result-area").text(result)
			}
			if ($("#output-format-select").val() == 3) {  // Map output
				$("#result-area").text(result)
				// Remove old layer from map
				if (mapFeatureDict["result"]) {
					removeMultiFeature(mapFeatureDict["result"])
				}
				else {
					mapFeatureDict["result"] = []
				}
				// Draw new layer on map
				var wicket = new Wkt.Wkt();
				for (i in result){
					wktGeom = result[i]
					wicket.read(wktGeom);
					var feature = wicket.toObject();
					mapFeatureDict["result"][i] = feature;
					mapFeatureDict["result"][i].addTo(map);
				}
			}
		});
	}



// On ready function for listeners and stuff
$(document).ready( function () {
	// Set base url in query builder
	$("#base-url").val(baseUrl)

	// Crosshair cursor on map
	L.DomUtil.addClass(map._container, 'crosshair-cursor-enabled');

	// Buttons
	$("#browser-location-as-origin").on( "click", function( event ) {  getLocation(); });
	$("#origin-location-from-map").on( "click", function( event ) {  if (mapFeatureDict["browser"]) { map.removeLayer(mapFeatureDict["browser"]); }; activateCoordsFromMap("origin"); });
	$("#destination-location-from-map").on( "click", function( event ) {  activateCoordsFromMap("destination"); });
	$("#send-request-button").on("click", function( event ) { sendRequest() })
	
	// Query builder listeners
	$("#api-function-select").on( "change", function( event ) {  
		if ($("#api-function-select").val() == "p2p") {
			$(".documentation-text").hide()
			$("#p2p-doc").show()
			$("#query-builder-container span").hide()
			$("#destination-location-from-map").show()
			$(".p2p-option").show()
					}
					else if ($("#api-function-select").val() == "ich") {
			$(".documentation-text").hide()
			$("#ich-doc").show()
			$("#query-builder-container span").hide()
			$("#destination-location-from-map").hide()
			$(".ich-option").show()
		}
	});
	$("#api-function-select").change()  // Update view
	$("#help-button").click();
});

		
