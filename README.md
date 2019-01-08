# pyRouting
This Project aims to provide an Rest API for the calculation of routes (also isochrones + more to follow) on top of OSM data.

<b>Notice: This project is experimental and under active development right now, meaning refactoring, restructuring, etc will occur. Query format will most certainly change as well. Also the scope is not clear yet so it will probably end up being a more generic geo api which also provides services like isochrone calculation, etc</b>

<h2>General Info</h2>
The API is built in Flask and utilizes PostgreSQL with the extensions PostGIS and pgRouting to perform the spatial calculations. The routing graph is created via osm2po right now as it is able to process a whole planet.pbf dump file (https://planet.osm.org/pbf/planet-latest.osm.pbf) in one run.

For portablility and ease of use the whole framework can be deployed using docker.
