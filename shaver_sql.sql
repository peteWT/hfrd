drop table if exists sce_units;

create table sce_units as with foo as (
       	     select st_buffer(st_concavehull(st_collect(wkb_geometry), .99),30) geom, 
       	      	    st_concavehull(st_collect(wkb_geometry), .99) bnd 
	     from shaverlake_units) 
	select wkb_geometry geom 
	from unit_boundaries 
	union 
	select st_exteriorring(geom) geom 
	from foo 
	union 
	select st_exteriorring(bnd) geom 
	from foo
	union
	select st_exteriorring((st_dump(st_union(st_intersection(s.wkb_geometry, st_buffer(st_envelope(u.wkb_geometry), 200))))).geom) geom
	from sierranf_cb s, shaverlake_units u ;
--	union
--	select st_exteriorring(the_geom) geom 
--	from sce_rdbuf;


alter table sce_units add column gid serial primary key;

select droptopology('sce_units_topo');
select createtopology('sce_units_topo', 3741);
select addtopogeometrycolumn('sce_units_topo', 'public', 'sce_units', 'topo_geom','LINE');
update sce_units set topo_geom = totopogeom(geom,'sce_units_topo',1, 5.0);

drop table if exists sce_clean;

create table sce_clean as with foo as (
       	     select st_getfacegeometry('sce_units_topo',face_id) geom 
       	     from sce_units_topo.face 
       	     where face_id >0)
	select 'SL_'||o.ogc_fid::text hfrd_uid, 
	       foo.geom, 
	       o.equipment, 
	       o.eqip_link, 
	       o.equip_link2,
	       st_area(foo.geom)*0.000247105 acres 
	from foo, shaverlake_units o 
	where st_contains(foo.geom, st_centroid(o.wkb_geometry));


