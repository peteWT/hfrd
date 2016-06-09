drop table if exists equipment;

create table equipment (mfg text,
		       model text,
		       descr text,
		       net_hp real,
		       ccase_cap real,
		       oilch_hrs real,
		       cost_standard real,
		       att_descr text,
		       att_cost real,
		       misc_descr text,
		       misc_cost real);

drop table if exists prelim;

create table prelim (mfg text,
		    model text,
       	     	    init_invest real,
		    salvage_vlaue real,
		    economic_life real,
		    sched_op_time real,
		    prod_time real,
		    ut_rate real,
		    pmh real);

drop table if exists fixed;

create table fixed (mfg text,
		    model text,
		    av_ann_dep real,
		    dep_method text,
		    avi real,
		    interest real,
		    insurance real,
		    taxes real);

drop table if exists op;

create table op (mfg text,
       	     	model text,
		    m_r real,
		    fuel real,
		    lubricants real,
		    tires real,
		    labor real);
