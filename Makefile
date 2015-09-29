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
buffsize := 100
nixHost := ~/host/hfrdgis/

db:
	createdb ${dbname}
	psql -d ${dbname} -c 'create extension postgis;'
	psql -d ${dbname} -c 'create extension postgis_topology;'
	psql -d ${dbname} -c 'create language plpython2u;'
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
db/slopecat:
	python -c 'import slope as s; s.slopecat()'
	touch $@


.PHONY: struct
struct: db products src_data db/usgs_srid db/lemmasrid db/slopecat

### Shaver Lake 
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

products/shaver_slope.geojson:
	wget ${demUrl}${sceDem}.zip
	unzip ${sceDem}.zip -d src_data
	rm ${sceDem}.zip
	python -c "import slope as sl; sl.slopeVector('shaver', 'products/shaver_projarea.geojson', 'src_data/img${sceDem}_13.img')"
	rm -f $@
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select p.geom,value,cl,ch, cl||'-'||ch||'%' as slope_range from shaver_projareaslope p join slopecat on(value=index)"

products/shaver_projarea.geojson: shaver
	${PG} -c "drop table if exists sce_projarea; create table sce_projarea as select st_buffer(st_concavehull(st_collect(wkb_geometry), .99),${buffsize}) geom from shaverlake_units;"
	rm -f $@
	ogr2ogr -overwrite -t_srs "${usgsproj4}" -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select st_buffer(st_concavehull(st_collect(wkb_geometry), .99),${buffsize}) geom from shaverlake_units"

products/sce_vegst.geojson: products/shaver_projarea.geojson
	gdalwarp -q -overwrite -cutline "PG:dbname=${dbname}" -csql "select st_transform(st_buffer(st_concavehull(st_collect(geom), .99),${buffsize}),${lemmaSrid}) geom from sce_clean" -crop_to_cutline -t_srs EPSG:${srid} -of GTiff /home/user/host/Downloads/gnn_sppsz_2014_08_28/mr200_2012/w001001.adf src_data/gnn_shaver.tif
	gdal_polygonize.py src_data/gnn_shaver.tif -f PostgreSQL "PG:dbname=${dbname}" sce_veg 
	${PG} -c 'delete from sce_veg where dn=0;'
	${PG} -c 'delete from sce_veg where dn is null;'
	${PG} -f vegstrata.sql
	ogr2ogr -overwrite  -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" sce_vegstrata

products/sce_plots:
	shp2pgsql -s 4326:3741 -d -I ${nixHost}SCE/SCE_GPS_Measurements/plots_812/hfrd/shaver_plots.shp sce_812_plots | psql -d hfrd
	shp2pgsql -s 3741 -d -I ${nixHost}SCE/SCELib/plots/sce_plots.shp sce_plots | psql -d hfrd
	psql -d ${dbname} -v t='sce_plots' -f sce_plots.sql
	pgsql2shp -f $@.shp hfrd 'select * from sce_plots p'
	zip $@.zip $@.*
	rm $@.geojson
	ogr2ogr -overwrite  -t_srs EPSG:4326 -f GeoJSON $@.geojson PG:"dbname=${dbname}" "sce_plots"

.PHONY: shaver
shaver: products/sce_clean.geojson db/shaver_road products/shaver_slope.geojson




## Santa Rosa
products/sr_nrcs_units.geojson:
	rm -f $@
	shp2pgsql -s 26911:${srid} -d -I -S "SantaRosa/Demo_Project_area.shp" sr_units | ${PG}
	ogr2ogr -overwrite  -f GeoJSON $@ PG:"dbname=${dbname}" "sr_nrcs_units"

products/sr_projarea.geojson: products/sr_units.geojson
	rm -f $@
	ogr2ogr -overwrite -t_srs "${usgsproj4}" -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select st_buffer(st_concavehull(st_collect(geom), .99),${buffsize}) geom from sr_units"

products/sr_clean.geojson: products/sr_nrcs_units.geojson
	${cdb2local} "CartoDB:biomass tables=sr_nrcs_units"
	${cdb2local} "CartoDB:biomass tables=sr_mech_unit_bnd"
	${cdb2local} "CartoDB:biomass tables=sr_tss_units"
	${PG} -f santa_rosa.sql
	ogr2ogr -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "sr_clean"

products/santarosa_slope.geojson:
	wget ${demUrl}${srDem}.zip
	unzip ${srDem}.zip -d src_data
	rm ${srDem}.zip
	python -c "import slope as sl; sl.slopeVector('santarosa', 'products/sr_projarea.geojson', 'src_data/img${srDem}_13.img')"
	rm -f $@
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select p.geom,value,cl,ch, cl||'-'||ch||'%' as slope_range from sr_projareaslope p join slopecat on(value=index)"
	touch $@

.PHONY: santa_rosa
santa_rosa: products/sr_clean.geojson products/sr_projarea.geojson products/santarosa_slope.geojson products/sr_nrcs_units.geojson

##Big Bear
products/bb_projarea.geojson: db db/usgs_srid
	shp2pgsql -s 26911:${srid} -d -I -S "Mountain Top/Equipment Units.shp" bb_eunits | ${PG}
	${PG} -c "drop table if exists bb_projarea; create table bb_projarea as select 1 gid, 'project boundary'::text descr, st_buffer(st_concavehull(st_collect(geom), .99),${buffsize}) geom, st_transform(st_buffer(st_concavehull(st_collect(geom), .99),${buffsize}),${usgssrid} ) ${usgsGeo} from bb_eunits;"
	rm -f $@
	ogr2ogr -overwrite -t_srs "${usgsproj4}" -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select gid, ${usgsGeo} from bb_projarea"

db/bb_strata:
	shp2pgsql -s 26911:${srid} -d -I  "Mountain Top/Demo_3.shp" bb_tlevel | ${PG}
	shp2pgsql -s 26911:${srid} -d -I  "Mountain Top/Demo_RCA.shp" bb_rca | ${PG}

products/bb_rca.geojson:
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select st_force2d((st_dump(geom)).geom) geom from bb_rca"

products/bb_tlevel.geojson:
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select st_force2d((st_dump(geom)).geom) geom from bb_tlevel"


products/bb_eunits.geojson:
	rm -f $@
	ogr2ogr -overwrite -preserve_fid -t_srs "${usgsproj4}" -f GeoJSON $@ PG:"dbname=${dbname}" -sql "select geom, gid, equipment from bb_eunits"

products/bb_slope.geojson: products/bb_projarea.geojson
	wget ${demUrl}${bbDem}.zip
	unzip ${bbDem}.zip -d src_data
	rm ${bbDem}.zip
	python -c "import slope as sl; sl.slopeVector('bigbear', 'products/bb_projarea.geojson', 'src_data/img${bbDem}_13.img')"
	rm -f $@
	ogr2ogr -overwrite -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" -sql  "select p.geom,value,cl,ch, cl||'-'||ch||'%' as slope_range from bb_projareaslope p join slopecat on(value=index)"

db/bb_gnnveg:
	gdalwarp -q -overwrite -cutline "PG:dbname=${dbname}" -csql "select st_transform(st_buffer(st_concavehull(st_collect(geom), .99),${buffsize}),${lemmaSrid}) geom from bb_projarea" -crop_to_cutline -t_srs EPSG:${srid} -of GTiff /home/user/host/Downloads/gnn_sppsz_2014_08_28/mr200_2012/w001001.adf src_data/gnn_bb.tif
	gdal_polygonize.py src_data/gnn_bb.tif -f PostgreSQL "PG:dbname=${dbname}" bb_veg 
	${PG} -c 'delete from bb_veg where dn=0;'
	${PG} -c 'delete from bb_veg where dn is null;'
	touch $@

products/bb_clean.geojson:
	${cdb2local} "CartoDB:biomass tables=bb_equip_assign"
	${cdb2local} "CartoDB:biomass tables=bb_boundaries"
	${PG} -f bb_clean.sql
	ogr2ogr -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "bb_clean"

products/bb_strata.geojson:
	${cdb2local} "CartoDB:biomass tables=bb_tlev_bnd"
	${cdb2local} "CartoDB:biomass tables=bb_tlevel_poly"
	${PG} -f bb_strata.sql
	ogr2ogr -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "bb_s_strata"

products/bb_plots.geojson:
	${PG} -c "drop table if exists bb_plots; create table bb_plots as with foo as (select hfrd_uid, st_buffer(geom, -12) geom from bb_s_strata) select randompointsinpolygon(geom,4), hfrd_uid, generate_series(1,4) spid from foo where st_area(geom) > 144; alter table bb_plots add column pid serial primary key; update bb_plots set hfrd_uid = hfrd_uid||'_'||pid||'_'||spid"
	pgsql2shp -r -f products/bb_plots.shp ${dbname} bb_plots
	ogr2ogr -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" "bb_plots"
.PHONY: plots
plots : products/bb_clean.geojson products/bb_strata.geojson products/bb_plots.geojson
## Vegstrata.sql is conficured for shaver. do not use...
products/bb_vegst.geojson:db/bb_gnnveg
	${PG} -f bb_vegstrata.sql
	ogr2ogr -overwrite  -t_srs EPSG:4326 -f GeoJSON $@ PG:"dbname=${dbname}" sce_vegstrata
https://biomass.cartodb.com/api/v2/sql?filename=bb_clean&q=select+*+from+sce_clean&format=shp

.PHONY: bigbear
bigbear: products/bb_slope.geojson products/bb_eunits.geojson products/bb_projarea.geojson

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

db/gnn_live: src_data/lemma_live.csv src_data/lemma_fields.csv src_data/lemma_codes.csv db/lemmasrid
	python -c "import pandas as pd, util;ce=util.eng();df=pd.read_csv('src_data/lemma_live.csv');df.columns=[i.lower() for i in df.columns];df.to_sql('gnn_live', ce, if_exists='replace')"
	python -c "import pandas as pd, util;ce=util.eng();df=pd.read_csv('src_data/lemma_codes.csv');df.columns=[i.lower() for i in df.columns];df.to_sql('gnn_codes', ce, if_exists='replace')"
	python -c "import pandas as pd, util;ce=util.eng();df=pd.read_csv('src_data/lemma_fields.csv');df.columns=[i.lower() for i in df.columns];df.to_sql('gnn_fields', ce, if_exists='replace')"
	touch $@


### In-situ data
db/allometry:
	python allo.py
	touch $@

db/insitu:
	python insitu.py
	touch $@

### Plot GPS




