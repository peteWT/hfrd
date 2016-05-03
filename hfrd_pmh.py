import miyata as miy

for idx in miy.costData.index:
    idr = miy.costData.ix[idx]
    miy.DpAsset.hp = idr['ratedhorsepower']
    miy.DpAsset.P = idr['equipmentcostwithstandardattachments']+\
                    idr['optionalattachmentcost']
    miy.DpAsset.N = idr['economiclife']
    miy.
