cartoApiKey := de4010605157fa8779dfe50c6f86f5cacf9c77fa
cartoUname := biomass
dbname := hfrd
srid := 3741
usgssrid := 98226
cdb2local := ogr2ogr -overwrite -progress -t_srs EPSG:${srid} -f "PostgreSQL" PG:"dbname=${dbname}"
PG := psql -d ${dbname}
road_buffer := 3
bbDem := n35w117
sceDem := n38w120
srDem := n34w117
demUrl := ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/13/IMG/
usgsGeo := geom_usgs
usgsproj4 := +proj=longlat +ellps=GRS80 +no_defs
lemmaSrid := 5070

db:
	createdb ${dbname}
	psql -d ${dbname} -c 'create extension postgis;'
	psql -d ${dbname} -c 'create extension postgis_topology;'
	mkdir $@

products:
	mkdir $@

src_data:
	mkdir $@

db/functions:
	${PG} -f functions.sql

db/usgs_srid:
	${PG} -f usgs_srid.sql
	touch $@

db/lemmasrid:
	${PG} -c 'delete from spatial_ref_sys where srid=5070;'
	curl http://epsg.io/5070.sql | ${PG}
	touch $@

.PHONY: struct
struct: db products src_data db/usgs_srid db/lemmasrid

products/sce_clean.geojson: db/shaver_road
	${cdb2local} "CartoDB:biomass tables=shaverlake_units"
	${cdb2local} "CartoDB:biomass tables=unit_boundaries"
	${cdb2local} "CartoDB:biomass tables=sierranf_cb"
	${PG} -f shaver_sql.sql
	ogr2ogr -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "sce_clean"

db/shaver_road:
	${cdb2local} "CartoDB:biomass tables=sce_road"
	${PG} -c 'drop table if exists sce_rdbuf; create table sce_rdbuf as select ogc_fid, st_buffer(wkb_geometry,${road_buffer}) the_geom, ${road_buffer} buf_dist from sce_road;'
	touch $@

.PHONY: shaver
shaver: products/sce_clean.geojson db/shaver_road

db/slopecat:
	python -c 'import slope as s; s.slopecat()'
	touch $@

products/bb_slope.geojson:db/bb_projarea
	wget ${demUrl}${bbDem}.zip
	unzip ${bbDem}.zip -d src_data
	rm ${bbDem}.zip
	python -c "import slope as sl; sl.slopeVector('bigbear', 'products/bb_projarea.geojson', 'src_data/img${bbDem}_13.img')"
	rm -f $@
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql  "select p.geom,value,cl,ch, cl||'-'||ch||'%' as slope_range from bb_projareaslope p join slopecat on(value=index)"

products/shaver_slope.geojson:
	wget ${demUrl}${sceDem}.zip
	unzip ${sceDem}.zip -d src_data
	rm ${sceDem}.zip
	python -c "import slope as sl; sl.slopeVector('shaver', 'products/shaver_projarea.geojson', 'src_data/img${sceDem}_13.img')"
	rm -f $@
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select p.geom,value,cl,ch, cl||'-'||ch||'%' as slope_range from shaver_projareaslope p join slopecat on(value=index)"


products/santarosa_slope.geojson:
	wget ${demUrl}${srDem}.zip
	unzip ${srDem}.zip -d src_data
	rm ${srDem}.zip
	python -c "import slope as sl; sl.slopeVector('santarosa', 'products/sr_projarea.geojson', 'src_data/img${srDem}_13.img')"
	rm -f $@
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select p.geom,value,cl,ch, cl||'-'||ch||'%' as slope_range from sr_projareaslope p join slopecat on(value=index)"
	touch $@

.PHONY: elev
elev: db/slopecat products/santarosa_slope.geojson products/shaver_slope.geojson products/bb_slope.geojson

products/bb_projarea.geojson: db db/usgs_srid
	shp2pgsql -s 26911:${srid} -d -I -S "Mountain Top/Equipment Units.shp" bb_eunits | ${PG}
	${PG} -c "drop table if exists bb_projarea; create table bb_projarea as select 1 gid, 'project boundary'::text descr, st_concavehull(st_collect(geom), .99) geom, st_transform(st_buffer(st_concavehull(st_collect(geom), .99),100),${usgssrid} ) ${usgsGeo} from bb_eunits;"
	rm -f $@
	ogr2ogr -overwrite -t_srs "${usgsproj4}" -f GeoJSON $@ PG:"dbname=${dbname}" "bb_projarea"

products/shaver_projarea.geojson: shaver
	rm -f $@
	ogr2ogr -overwrite -t_srs "${usgsproj4}" -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select st_buffer(st_concavehull(st_collect(wkb_geometry), .99),100) geom from shaverlake_units"



.PHONY: proj_bnd
prj_bnd: products/bb_projarea.geojson products/shaver_projarea.geojson products/bb_projarea.geojson


## Santa Rosa
products/sr_units.geojson:
	rm -f $@
	shp2pgsql -s 26911:${srid} -d -I -S "SantaRosa/Demo_Project_area.shp" sr_units | ${PG}
	ogr2ogr -overwrite  -f GeoJSON $@ PG:"dbname=${dbname}" "sr_units"

products/sr_projarea.geojson: products/sr_units.geojson
	rm -f $@
	ogr2ogr -overwrite -t_srs "${usgsproj4}" -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select st_buffer(st_concavehull(st_collect(geom), .99),100) geom from sr_units"

##LEMMA Veg Data
src_data/lemma_live.csv:
	mdb-export ~/host/Downloads/db_sppsz_2014_04_21.mdb  SPPSZ_ATTR_LIVE > $@

src_data/lemma_fields.csv:
	mdb-export ~/host/Downloads/db_sppsz_2014_04_21.mdb  Metadata_fields > $@
db/plants:
	python -c "import pandas as pd, util;ce=util.eng();df=pd.read_csv('http://plants.usda.gov/java/downloadData?fileName=plantlst.txt&static=true');df.columns=[i.lower().replace(' ','') for i in df.columns];df.to_sql('plants', ce, if_exists='replace')"
	touch $@

src_data/lemma_codes.csv:
	mdb-export ~/host/Downloads/db_sppsz_2014_04_21.mdb  Metadata_codes > $@

db/gnn_live: src_data/lemma_live.csv src_data/lemma_fields.csv src_data/lemma_codes.csv
	python -c "import pandas as pd, util;ce=util.eng();df=pd.read_csv('src_data/lemma_live.csv');df.columns=[i.lower() for i in df.columns];df.to_sql('gnn_live', ce, if_exists='replace')"
	python -c "import pandas as pd, util;ce=util.eng();df=pd.read_csv('src_data/lemma_codes.csv');df.columns=[i.lower() for i in df.columns];df.to_sql('gnn_codes', ce, if_exists='replace')"
	python -c "import pandas as pd, util;ce=util.eng();df=pd.read_csv('src_data/lemma_fields.csv');df.columns=[i.lower() for i in df.columns];df.to_sql('gnn_fields', ce, if_exists='replace')"
	touch $@


### Veg types

products/sce_vegst.geojson: products/shaver_projarea.geojson
	gdalwarp -q -overwrite -cutline "PG:dbname=${dbname}" -csql "select st_transform(st_buffer(st_concavehull(st_collect(geom), .99),100),${lemmaSrid}) geom from sce_clean" -crop_to_cutline -t_srs EPSG:${srid} -of GTiff /home/user/host/Downloads/gnn_sppsz_2014_08_28/mr200_2012/w001001.adf src_data/gnn_shaver.tif
	gdal_polygonize.py src_data/gnn_shaver.tif -f PostgreSQL "PG:dbname=${dbname}" sce_veg 
	${PG} -c 'delete from sce_veg where dn=0;'
	${PG} -c 'delete from sce_veg where dn is null;'
	${PG} -f vegstrata.sql
	ogr2ogr -overwrite  -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" sce_vegstrata


