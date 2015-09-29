drop table if exists bb_strata;

create table bb_strata as 
	select wkb_geometry from bb_tlev_bnd
	union
	select wkb_geometry from bb_boundaries;




alter table bb_strata add column gid serial primary key;

select droptopology('bb_strata_topo');
select createtopology('bb_strata_topo', 3741);
select addtopogeometrycolumn('bb_strata_topo', 'public', 'bb_strata', 'topo_geom','LINE');
update bb_strata set topo_geom = totopogeom(st_force2d(wkb_geometry),'bb_strata_topo',1, 5.0);

drop table if exists bb_s_strata;

create table bb_s_strata  as with foo as 
       	     (select st_getfacegeometry('bb_strata_topo',face_id) geom
       	     from bb_strata_topo.face 
       	     where face_id >0)
	     select o.hfrd_uid||'_tl'||trt_lvl::text hfrd_uid, 
	     	    foo.geom,
		    o.hfrd_uid equip_uid,
		    o.name,
		    t.trt_lvl
	     from foo,
	     bb_clean o,
	     bb_tlevel_poly t
	     where st_contains(st_buffer(o.geom, 5), foo.geom)
	     and st_within(st_centroid(foo.geom),t.wkb_geometry);
--	     and st_contains(st_buffer(t.wkb_geometry, 5), foo.geom);
--	     where st_within(st_centroid(foo.geom),o.geom)
--	     and st_within(st_centroid(foo.geom),t.wkb_geometry);


