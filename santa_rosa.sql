drop table if exists sr_units;

create table sr_units as select wkb_geometry from sr_mech_unit_bnd;
-- create table sr_units as with foo as (
--        	     select st_buffer(st_concavehull(st_collect(wkb_geometry), .99),30) geom, 
--        	      	    st_concavehull(st_collect(wkb_geometry), .99) bnd 
-- 	     from sr_nrcs_units) 
-- 	select  wkb_geometry
-- 	from sr_mech_unit_bnd 
-- 	union 
-- 	select st_exteriorring(geom) geom 
-- 	from foo 
-- 	union 
-- 	select st_exteriorring(bnd) geom 
-- 	from foo;
	-- union
	-- select st_exteriorring((st_dump(st_union(u.wkb_geometry))).geom) geom
	-- from sr_nrcs_units u;



alter table sr_units add column gid serial primary key;

select droptopology('sr_units_topo');
select createtopology('sr_units_topo', 3741);
select addtopogeometrycolumn('sr_units_topo', 'public', 'sr_units', 'topo_geom','LINE');
update sr_units set topo_geom = totopogeom(wkb_geometry,'sr_units_topo',1, 5.0);

drop table if exists sr_clean;

create table sr_clean  as with foo as 
       	     (select st_getfacegeometry('sr_units_topo',face_id) geom
       	     from sr_units_topo.face 
       	     where face_id >0)
	     select 'SR_'||o.ogc_fid::text hfrd_uid , 
	     	    foo.geom,
		    o.mfg,
		    o.model
	     from foo,
	     	  sr_tss_units o
	     where st_contains(foo.geom, st_centroid(o.wkb_geometry));




