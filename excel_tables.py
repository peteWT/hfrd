import pandas as pd
import sqlite3

con = sqlite3.connect('hfrd_machinecost.db')
excel_file = 'machine_cost_tables.xlsx'
xl_wrt = pd.ExcelWriter(excel_file,engine='xlsxwriter')

#Summary table
summary = pd.read_sql_query("select mfg 'Manufacturer', model 'Model', init_invest 'Initial investment ($)', salvage_vlaue 'Salvage Value($)', economic_life 'Economic Life (years)', sched_op_time 'Scheduled Operating Time (hrs/year)', prod_time 'Productive Time (hrs/year)', ut_rate 'Utilization Rate', pmh 'Use Cost ($/PMH)' from prelim", con)
summary.to_excel(xl_wrt, 'Summary Costs', index=False)



#Operating costs table
op = pd.read_sql_query("select mfg 'Manufacturer', model 'Model', m_r 'Maintenance and Repairs ($/hr)', fuel 'Fuel ($/hr)', lubricants 'Lubricants ($/hr)', tires 'Tire/track ($/hr)', labor 'Wages ($/hr)'  from op;", con)
op.to_excel(xl_wrt, 'Operating Costs', index=False)


#Equipment cost table
equip = pd.read_sql_query("select mfg 'Manufacturer', model 'Model', descr 'Description', net_hp 'Power (hp)', ccase_cap 'Crank case capacity (gal)', oilch_hrs 'Hours between oil change', cost_standard 'Prime mover cost', att_cost+misc_cost 'Attachment cost' from equipment;", con)
equip.to_excel(xl_wrt, 'Equipment', index=False)

#fixed cost table
fixed = pd.read_sql_query("select mfg 'Manufacturer', model 'Model', av_ann_dep 'Annual Depreciation', interest 'Annual Interest', insurance 'Annual Insurance', taxes 'Annual Taxes' from fixed;",con)
fixed.to_excel(xl_wrt, 'Fixed Costs', index=False)



xl_wrt.save()
