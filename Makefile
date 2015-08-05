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


db:
	createdb ${dbname}
	psql -d ${dbname} -c 'create extension postgis;'
	psql -d ${dbname} -c 'create extension postgis_topology;'
	mkdir $@

products:
	mkdir $@

src_data:
	mkdir $@

db/usgs_srid:
	${PG} -f usgs_srid.sql
	touch $@

.PHONY: struct
struct: db products src_data db/usgs_srid

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
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "bb_projareaslope"

products/shaver_slope.geojson:
	wget ${demUrl}${sceDem}.zip
	unzip ${sceDem}.zip -d src_data
	rm ${sceDem}.zip
	python -c "import slope as sl; sl.slopeVector('shaver', 'products/shaver_projarea.geojson', 'src_data/img${sceDem}_13.img')"
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "shaver_projareaslope"


products/santarosa_slope.geojson:
#	wget ${demUrl}${srDem}.zip
#	unzip ${srDem}.zip -d src_data
#	rm ${srDem}.zip
	python -c "import slope as sl; sl.slopeVector('santarosa', 'products/sr_projarea.geojson', 'src_data/img${srDem}_13.img')"
	rm -f $@
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "sr_projareaslope"
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
