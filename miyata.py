import util as ut
from operator import sub

costData = ut.gData(
    '1TsHo2wyvzKYugiDudPHFJjtFS--5ZBcWNb2gGopteX4',
    1475511425)
constants = ut.gData(
    '1TsHo2wyvzKYugiDudPHFJjtFS--5ZBcWNb2gGopteX4',
    1199790733)
fedtx, ltx, freight, salv, life, sophr, ptime = [constants.iloc[i].to_dict() for i in range(len(constants))]

# ## Depreciation


class DpAsset:
    """Calcultaing depreciation of an asset"""

    def __init__(self):
        '''
        default variables for depreciation calculations
        n = Economic life of the equipment -- default is 5 years
        p = Initial Investment -- default is $85,000
        s = Salvage value --- default is 20% of p
        '''
        self.n = 5.0
        self.p = 85000.00
        self.s = 0.2
        self.dbMultiplier = 2.0

    def sVal(self, arbitrary=None):
        if arbitrary is not None:
            return arbitrary
        else:
            return self.s*self.p

    def depRate(self):
        '''
        Depreciation Rate
        -----------------
        n: economic life in years
        '''
        return 1.0/self.n

    def depStraitLine(self, sval=None):
        '''
        Strait line method
        ------------------
        p: innital investment cost of equipment
        s: salvage value
        n: economic life in years
        '''
        if sval is None:
            salvage = self.sVal()
        else:
            salvage = self.sVal(arbitrary=sval)
        return (self.p-salvage)/self.n

    def depDecBalance(self):
        '''Declining balance method'''
        sched = {}
        undepValue = self.p
        annDep = 0
        for year in range(int(self.n)):
            sched['year' + str(year)] = (annDep, undepValue)
            annDep = undepValue * (self.depRate() * self.dbMultiplier)
            undepValue = undepValue - annDep
        return sched

    def depSOYD(self, sval = None):
        '''Sum-of-years-digits method'''
        if sval is None:
            salvage = self.sVal()
        else:
            salvage = self.sVal(arbitrary=sval)
        sched = {}
        undepValue = self.p
        tDep = self.p - salvage
        annDep = 0
        sched['year0'] = (annDep, undepValue)
        years = range(1, int(self.n) + 1)
        revyears = sorted(years, reverse=True)
        for y in range(len(years)):
            annDep = tDep * revyears[y]/sum(years)
            undepValue = undepValue - annDep
            sched['year' + str(years[y])] = (annDep, undepValue)
        return sched


class MyTime:

    def __init__(self):
        '''
        default variables for time calculations
        SH = shceduled time
        H = productive time
        '''
        self.capFactor = 0.9
        self.hrsPerDay = 8
        self.annWorkDays = 5*52*self.hrsPerDay
        self.SH = self.capFactor * self.annWorkDays
        self.utRate = {"Chain saw-straight blade": 0.5,
                       "Chain saw-bow blade": 0.5,
                       "Big stick loader": 0.9,
                       "Shortwood hydraulic loader": 0.65,
                       "Longwood hydraulic loader": 0.64,
                       "Uniloader": 0.6,
                       "Frontend loader": 0.6,
                       "Cable skidder": 0.67,
                       "Grapple skidder": 0.67,
                       "Shortwood prehauler Longwood prehauler": 0.64,
                       "Feller-buncher": 0.65,
                       "Chipper": 0.75,
                       "Slasher": 0.67}

    def H(self, equipU='Grapple skidder'):
        return self.SH * self.utRate[equipU]
