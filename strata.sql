drop table if exists sce_strata;

create table sce_strata as with inter as (
       	     	select st_intersection(e.geom, st_transform(s.geom,3741)) geom, 
		       c.cl,
		       c.ch,
		       e.hfrd_uid,
		       'hfrd_'||e.hfrd_uid::text||'_'||c.cl::text||c.ch::text st_code
		from sce_clean e, 
		     shaver_projareaslope s 
		join slopecat c on(s.value=c.index)
		where st_area(st_intersection(e.geom, st_transform(s.geom,3741)))/0.000247>1
		)
	select st_union(inter.geom),
	       inter.st_code
	from inter
	group by inter.st_code;
