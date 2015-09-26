drop table if exists bb_units;

create table bb_units as 
	select wkb_geometry from bb_boundaries;




alter table bb_units add column gid serial primary key;

select droptopology('bb_units_topo');
select createtopology('bb_units_topo', 3741);
select addtopogeometrycolumn('bb_units_topo', 'public', 'bb_units', 'topo_geom','LINE');
update bb_units set topo_geom = totopogeom(st_force2d(wkb_geometry),'bb_units_topo',1, 5.0);

drop table if exists bb_clean;

create table bb_clean  as with foo as 
       	     (select st_getfacegeometry('bb_units_topo',face_id) geom
       	     from bb_units_topo.face 
       	     where face_id >0)
	     select 'BB_'||o.ogc_fid::text hfrd_uid , 
	     	    foo.geom,
		    o.name
	     from foo,
	     	  bb_equip_assign o
	     where st_contains(foo.geom, o.wkb_geometry);



