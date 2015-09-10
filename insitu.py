import util as ut

mDataKey = '1RNcXXvO5d8JFmPCEn_u7Qy30MCsg4kKUBMyjYW-swUk'
sheets = {'treedata':350897684,
          'sitedescrip':0,
          'fuels': 962428416,
          'soils': 983196900,
          'metadata': 1686733598,
          'seedling': 2141390901,
          'sapling': 1728276363
          }

def biomass (h,dbh,a,b):
    



allometry = {'WO': {'cname':'white fir',
                   'sname': 'Abies concolor',
                   'alom_src': 
                   'globallom_id': 12323,
                   'meas_unit': 'cm',
                   'eqn': 1}}

tData = ut.gData(mDataKey, sheets['treedata'])
tData.to_sql('treedata', ut.eng(), if_exists = 'replace')
