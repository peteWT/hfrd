

delete from :t where plotid >30;
delete from :t where plotid in (22,23,24,25,29);
alter table :t add column est_date date;
update :t set est_date = '08-12-2015' where plotid<22;
update :t set est_date = '09-18-2015' where plotid in (26,27,28,30);

insert into :t (geom, hfrd_uid)(select randompointsinpolygon(st_buffer(geom, -23),2) geom, hfrd_uid from sce_clean);

update :t set plotid = gid where plotid is NULL;
update :t set est_date = '09-21-2015' where est_date is NULL;

