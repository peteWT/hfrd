import util as ut
import pandas as pd

url = 'http://www.fs.fed.us/ne/global/pubs/books/dia_biomass/'
tables = {'Table3_GTR-NE-319.xls': {'sheet' :1,
                                    'header':2},
          'Table4_GTR-NE-319.xls': {'sheet' :0,
                                    'header':2},
          'Table5_GTR-NE-319.xls': {'sheet' :0,
                                    'header':2},
          'Table6_GTR-NE-319.xls': {'sheet' :0,
                                    'header':2},
          'Table7_GTR-NE-319.xls': {'sheet' :0,
                                    'header':2},
          'Table9_GTR-NE-319.xls': {'sheet' :0,
                                    'header':2}}

for k in tables.keys():
    df = pd.read_excel(url+k,
                       sheetname=tables[k]['sheet'],
                       header = tables[k]['header'])
    df.columns = [i.replace(' ','').
                  replace('.','_').
                  replace('(','_').
                  replace(')','_').lower() for i in df.columns]
    df.to_sql(k.split('_')[0].lower(), ut.eng(), if_exists = 'replace')
