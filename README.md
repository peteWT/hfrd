Hazardous Fuels Reduction Project
=================================

## Estimating sampling intensity by stratum. 

I've based this on the instructions found in [this presentation](http://www.rainforestcoalition.org/TinyMceFiles/CD%20REDD%20II,%20May%202011/11%20Forest%20Inventory_SteffenLackmann.pdf)

Number of plots is determined based on:

1. target percent error (10%)
2. students t value for inf. degrees of freedom (1.96)
3. plot size (0.1 ac)
4. sampling frame area (derived from spatial data)
4. mean and standard deviation of the target metric with the sampling frame

Estimates of the varibility in biophysical parameters within the study site were derived from the [LEMMA](http://lemma.forestry.oregonstate.edu/data/plot-database) data. The function for calculating the number is called 'numplots' function found in ['functions.sql'](https://github.com/peteWT/hfrd/blob/master/functions.sql).

The following query estimates plot count across the frame at shaver lake based on variation in the `hcb' -- Height to Live Crown Base parameter in the LEMMA plot database

    select numplots(stddev(g.hcb)/avg(g.hcb),
			(st_area(c.geom)*0.0002471/0.1)::int) 
		from sce_projarea c, sce_veg v 
		join gnn_live g on(v.dn=g.fcid) 
		where st_intersects(c.geom, v.wkb_geometry) 
		group by c.geom;

results in 103 plots.

for the shaver equipment uints this results, based on this query:

    select hfrd_uid,
		round(103 * (st_area(u.geom)/st_area(f.geom))) plots_uid
	   from sce_clean u, sce_projarea f;

plots per unit are:

 hfrd_uid | plots_uid 
----------+-----------
 SL_11    |         3
 SL_10    |         4
 SL_5     |         9
 SL_4     |         5
 SL_1     |         3
 SL_3     |         8
 SL_9     |         5
 SL_2     |         5
 SL_8     |         4
 SL_6     |         2
 SL_7     |         7


