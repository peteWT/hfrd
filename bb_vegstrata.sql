drop table if exists bb_vegstrata; 

create table bb_vegstrata as 
       with vtype as (
       	    	  select 
       	    	  	 st_union(v.wkb_geometry) geom,
       		  	 g.fortypba 
		  	 from bb_veg v 
		  	 join gnn_live g on (v.dn=g.fcid)
		  	 group by g.fortypba
		)
		select
			st_union(vt.geom) geom,
			'other' veg_cat
		from vtype vt
		where vt.fortypba not in ('PIJE','QUKE','PIPO','ABGRC/PILA')
		union
		select
			vt.geom,
			vt.fortypba
		from vtype vt
		where vt.fortypba in ('PIJE','QUKE','PIPO','ABGRC/PILA')
;
