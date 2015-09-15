import grass_env as evt
import grass.script as gs
from grass.script import setup as gsetup
import os
from sqlalchemy import create_engine as ce
import pandas as pd

dbname = 'hfrd'
engine = ce('postgresql:///{0}'.format(dbname), echo=True)


def grassname(p):
    return os.path.basename(p).split('.')[0]


def slopecat(bk=[0, 15, 35, 65, 90]):
    cats = {1: [bk[0], bk[1]],
            2: [bk[1], bk[2]],
            3: [bk[2], bk[3]],
            4: [bk[3], bk[4]]}
    grassTxt = '{0}:{1}:{2}:{2}\n'
    f = open('slp_reclass', 'w+')
    for k in cats.keys():
        f.write(grassTxt.format(cats[k][0], cats[k][1], k))
    f.close()
    df = pd.DataFrame.from_dict(cats, orient='index')
    df.columns = ['cl', 'ch']
    df.to_sql('slopecat', engine, if_exists='replace')
    return cats


def slopeVector(mapset, bnd, erast):
    gsetup.init(evt.gisbase, evt.gisdb, 'socal_hfrd', mapset)
    slopecat()
    gs.parse_command('v.in.ogr',
                     flags='e',
                     input=bnd,
                     output=grassname(bnd),
                     overwrite=True,
                     verbose=True)
    gs.parse_command('g.region',
                     vect=grassname(bnd))
    gs.parse_command('r.in.gdal',
                     input=erast,
                     output=grassname(erast),
                     overwrite=True,
                     verbose=True)
    gs.parse_command('r.slope.aspect',
                     elevation=grassname(erast),
                     slope=grassname(erast)+'slp',
                     format='percent',
                     overwrite=True,
                     verbose=True)
    gs.parse_command('g.region',
                     rast=grassname(erast)+'slp')
    gs.parse_command('r.recode',
                     input=grassname(erast)+'slp',
                     output=grassname(erast)+'slprc',
                     rules='slp_reclass',
                     overwrite=True,
                     verbose=True)
    gs.parse_command('r.to.vect',
                     flags='s',
                     input=grassname(erast)+'slprc',
                     output=grassname(bnd)+'slope',
                     type_='area',
                     verbose=True,
                     overwrite=True)
    gs.parse_command('v.out.postgis',
                     input=grassname(bnd)+'slope',
                     output="PG:dbname=hfrd",
                     overwrite=True,
                     options="SRID=98226")
