import miyata as miy
import math
import numpy as np

results =[]

for idx in miy.costData.index:
    idr = miy.costData.ix[idx]
    miy.DpAsset.hp = idr['ratedhorsepower']
    miy.DpAsset.P = idr['equipmentcostwithstandardattachments'] +\
        idr['optionalattachmentcost.']
    miy.DpAsset.N = idr['economiclife']
    if math.isnan(idr['salvagevalue']) is False:
        miy.DpAsset.S = idr['salvagevalue']
    if math.isnan(idr['scheduledoperatingtime']) is False:
        miy.MiyTime.H(equipU=idr['scheduledoperatingtime'])
    if type(idr['depreciationmethod']) == float  or idr['depreciationmethod'] == 'strait line':
        dep = miy.DpAsset.depStraitLine()
    elif idr['depreciationmethod'] == 'declining balance':
        dep = np.mean([i[0] for i in miy.DpAsset.depDecBalance().values()])
    elif idr['depreciationmethod'] == 'supm of years digits':
        dep = np.mean([i[0] for i in miy.DpAsset.depSOYD().values()])
    results.append([idr['equipmentmodelnumber'], miy.fixedCost(dep, miy.DpAsset.AVI(), miy.DpAsset.IIT(), miy.MiyTime.H())])

    

