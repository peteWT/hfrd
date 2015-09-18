drop table if exists sce_plots;


create table sce_plots as
       select hfrd_uid,
       	      'pset2'::text round,
       	      randompointsinpolygon(geom,2) geom
	 from sce_clean;

