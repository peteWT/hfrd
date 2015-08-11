CREATE OR REPLACE FUNCTION makegrid(geometry, integer)
RETURNS geometry AS
'SELECT ST_Collect(ST_SetSRID(ST_POINT(x,y),ST_SRID($1))) FROM 
generate_series(floor(st_xmin($1))::int, ceiling(st_xmax($1)-st_xmin($1))::int, $2) as x
,generate_series(floor(st_ymin($1))::int, ceiling(st_ymax($1)-st_ymin($1))::int,$2) as y 
where st_intersects($1,ST_SetSRID(ST_POINT(x,y),ST_SRID($1)))'
LANGUAGE sql
