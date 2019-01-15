# Portable-Geo-API
This Project aims to provide an Rest API for the calculation of road network related analysis (routing, isochrones, etc) on top of OSM data.

<h2>General Info</h2>

The API is built in Flask and utilizes PostgreSQL with the extensions PostGIS and pgRouting to perform the spatial calculations. The routing graph is created via osm2po right now as it is able to process a whole planet.pbf dump file (https://planet.osm.org/pbf/planet-latest.osm.pbf) in one run.

For portablility and ease of use the whole framework can be deployed using docker.

<h2>Installation Notes</h2>

<h3>Optional: Backup your current DB</h3>

We use pg_dump to create a dumpfile from the shell:

```bash
pg_dump --format=c --create --no-owner --no-privileges --verbose --file=/OUTPUT/PATH/FOR/YOUR/DUMPFILE.dump --dbname=YOURDATABASENAME
```

<h3>Graph building</h3>

We use osm2po (http://osm2po.de/) to load the data into the database.

<i>Optional:The osm2po.config file is replaced to create a routing graph which is optimized for pedestrian routing:
Modified for current version of osm2po (5.2.43): https://github.com/dkuenzel/Portable-Geo-API/blob/master/osm2po/osm2po.config (Original osm2po configuration taken from Walkers guide schema: https://raw.githubusercontent.com/scheibler/WalkersGuide-Server/master/misc/osm2po_5.0.18.config)</i>

```bash
java -Xmx30g -jar osm2po-core-5.2.43-signed.jar prefix=world tileSize=45x45,1 ../planet-latest.osm.pbf
```

<h3>Create the target DB</h3>

<b>Warning: this will delete the existing DB!!</b>

```bash
DB="osm_routing"; 
dropdb $DB; 
createdb $DB; 

psql -d $DB -c "BEGIN; CREATE EXTENSION postgis; CREATE EXTENSION pgRouting; END;";
```
  
<h3>Data Loading</h3>

Load the osm2po output into the db in parallel (BaSH):
```bash
# target database name
DB="osm_routing"; 

# Create a common log file
logFile="/tmp/routing_sql.log"; 
rm $logFile; 
touch $logFile; 

IFS=$'\n'; 

for filename in $(ls -1 /THE/PATH/TO/YOUR/osm2po/OUTPUTFILES/*.sql); 
do 
  (psql -d osm_routing --quiet --file $filename 2>&1 | sed -e "s#^#$(date) ${filename} ($$): #g" | tee -a $logFile) & 
done;
```

<h3>DB ops</h3>

```sql
create extension postgis;
create extension pgRouting;
create index on world_2po_4pgr using gist (geom_vertex);
create index on world_2po_4pgr using gist (geom_way);
analyze world_2po_4pgr;
cluster world_2po_vertex using world_2po_vertex_geom_vertex_idx;
```

<h3>Run The API</h3>

* Adjust the configuration in `app/settings/` to match your database setup
* After deployment visit: http://yourhost:5000
