import miyata as miy
import math
import numpy as np
from tabulate import tabulate
import sqlite3

dbname = 'hfrd_machinecost.db'
f = open('results.md', 'w')
tables = open('cost_tables.sql', 'r').read()
con = sqlite3.connect(dbname)
con.executescript(tables)

eqip_insert = '''insert into equipment values(
'{mfg}',
'{mod}',
'{ds}',
{hp},
{ccase},
{oilch_hr},
{cost_v},
'{att_d}',
{att_cost},
'{misc_d}',
{misc_cost});'''.replace('\n', ' ')

prelim_insert = '''insert into prelim values(
'{mfg}',
'{mod}',
{ii},
{sv},
{econ_life},
{SH},
{Ht},
{ut},
{pmhr});
'''.replace('\n', ' ')

fixed_insert = '''insert into fixed values(
'{mfg}',
'{mod}',
{an_dep},
'{dp_m}',
{avinv},
{interest},
{insurance},
{taxes});
'''.replace('\n', ' ')

op_insert = '''insert into op values(
'{mfg}',
'{mod}',
{manr},
{fue},
{lubr},
{tir},
{lab});
'''.replace('\n', ' ')




results = {}

for idx in miy.costData.index:
    idr = miy.costData.ix[idx]
    miy.DpAsset.cCap = idr['lubricantreservoir']
    miy.DpAsset.cTime = idr['lubricanthours']
    miy.DpAsset.hp = idr['ratedhorsepower']
    print idr['equipmentmodelnumber']
    # Addup equipment attachments ann misc.
    miy.DpAsset.P = idr['equipmentcostwithstandardattachments'] +\
        np.nan_to_num(idr['optionalattachmentcost']) +\
        np.nan_to_num(idr['miscellaneous'])
    # If econmic life not reported use default (5 years)
    if math.isnan(idr['economiclife']) is False:
        miy.DpAsset.N = float(idr['economiclife'])
    # If salvage value not reported use default (20% of P)
    if math.isnan(idr['salvagevalue']) is False:
        miy.DpAsset.S = idr['salvagevalue']
    # If scheduled and actual operating hours are reported,
    # calculate a utilization rate. Otherwise use average
    # from all equiment reported in Miyata.
    if math.isnan(idr['scheduledoperatingtime']) is True or idr['productivetime'] / idr['scheduledoperatingtime'] == 1.0:
        utRt = miy.MiyTime.utRate()
    else:
        utRt = idr['productivetime'] / idr['scheduledoperatingtime']
    H = miy.MiyTime.H(utRt)

    # Set depreciation rate based on input.
    # If none selected, strait line is used.
    if type(idr['depreciationmethod']) == float or idr['depreciationmethod'] == 'strait line':
        dep = miy.DpAsset.depStraitLine()
    elif idr['depreciationmethod'] == 'declining balance':
        dep = np.mean([i[0] for i in miy.DpAsset.depDecBalance().values()])
    elif idr['depreciationmethod'] == 'supm of years digits':
        dep = np.mean([i[0] for i in miy.DpAsset.depSOYD().values()])
    fix = miy.fixedCost(dep,
                        miy.DpAsset.AVI(),
                        miy.DpAsset.IIT(),
                        H)
    op = miy.operatingCost(miy.DpAsset.hrFuelCost(),
                           miy.DpAsset.oLubeCost() + miy.DpAsset.qCost(),
                           miy.DpAsset.hTireCost(),
                           miy.DpAsset.maintCost(dep, H),
                           H)
    fm = fix['Fixed cost per H'] + op['Operating cost'][0]
    pmh = {'Labor cost hourly': [miy.DpAsset.wages],
           'Utilization rate': [utRt],
           '$/PMH': [fm + (miy.DpAsset.wages * utRt)]}

    equipText = {'Model Number': idr['equipmentmodelnumber'],
                 'Manufacturer': idr['equipmentmfg.'],
                 'Description': idr['equipmentdescription']}

    results[idr['equipmentmodelnumber']] = {'desc': equipText,
                                            'fixed': fix,
                                            'operating': op,
                                            'total_machine': fm,
                                            'Summary': pmh}
    # Create tables in the database
    con.execute(eqip_insert.format(mfg=equipText['Manufacturer'],
                                   mod=equipText['Model Number'],
                                   ds=equipText['Description'].replace("'","''"),
                                   hp=miy.DpAsset.hp,
                                   ccase=miy.DpAsset.cCap,
                                   oilch_hr=miy.DpAsset.cTime,
                                   att_d=idr['optionalattachment'],
                                   cost_v=idr['equipmentcostwithstandardattachments'],
                                   att_cost=np.nan_to_num(idr['optionalattachmentcost']),
                                   misc_cost=np.nan_to_num(idr['miscellaneous']),
                                   misc_d=' '))
    con.commit()
    con.execute(prelim_insert.format(mfg=equipText['Manufacturer'],
                                     mod=equipText['Model Number'],
                                     ii=miy.DpAsset.P,
                                     sv=miy.DpAsset.S,
                                     econ_life=miy.DpAsset.N,
                                     SH=miy.MiyTime.SH(),
                                     Ht=H,
                                     ut=utRt,
                                     pmhr=pmh['$/PMH'][0][0]))
    con.commit()
    con.execute(fixed_insert.format(mfg=equipText['Manufacturer'],
                                    mod=equipText['Model Number'],
                                    an_dep=dep,
                                    dp_m=idr['depreciationmethod'],
                                    interest=miy.DpAsset.AVI()*miy.DpAsset.intPct,
                                    insurance=miy.DpAsset.AVI()*miy.DpAsset.insPct,
                                    taxes=miy.DpAsset.AVI()*miy.DpAsset.taxPct,
                                    avinv=miy.DpAsset.AVI()))

    con.commit()
    con.execute(op_insert.format(mfg=equipText['Manufacturer'],
                                 mod=equipText['Model Number'],
                                 manr=miy.DpAsset.maintCost(dep, H),
                                 fue=miy.DpAsset.hrFuelCost(),
                                 lubr=miy.DpAsset.oLubeCost(),
                                 tir=miy.DpAsset.hTireCost(),
                                 lab=miy.DpAsset.wages))
    con.commit()

head = """
## {Manufacturer} {Model Number}\n
{Description}

"""
summary = """

### Summary

{}

"""

fixed = """
### Fixed Costs

{}

"""
oper = """
### Operating Costs

{}

"""
tmc = """
### Total Machine Costs

{}

"""

f.write('''# Hazardous fuels reduction demonstration equipment costs
Input data compiled from manufacturers or contractors and caclulated based on Miyata (1980)\n''')

for k in results.keys():
    f.write(head.format(**results[k]['desc']))
    f.write(summary.format(tabulate(results[k]['Summary'],
                                    headers='keys',
                                    tablefmt='pipe')))
    f.write(oper.format(tabulate(results[k]['fixed'],
                                 headers='keys',
                                 tablefmt='pipe')))
    f.write(tmc.format(tabulate(results[k]['operating'],
                                headers='keys',
                                tablefmt='pipe')))

f.write('''

## Reference

1. Miyata ES. Determining fixed and operating costs of logging equipment [Internet]. General Technical Report NC-55. 1980. Available from: [[http://www.nrs.fs.fed.us/pubs/gtr/gtr_nc055.pdf?]]

''')

f.close()
