delete from spatial_ref_sys where srid=98226;

INSERT into spatial_ref_sys (
       	    		    srid,
       	    		    auth_name, 
			    auth_srid, 
			    proj4text, 
			    srtext) 
		values (
		       98226, 
		       'sr-org',
		       8226, 
		       '+proj=longlat +ellps=GRS80 +no_defs ', 
		       'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.017453292519943295],VERTCS["Unknown VCS",VDATUM["Unknown"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]]'
		       );
