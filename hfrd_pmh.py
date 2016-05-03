import miyata as miy
import math

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

