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

foo = 36


def AVI(P, S, N):
    return (((P-S)*(N+1))/(2*N)) + S


class DpAsset:
    """Calcultaing depreciation of an asset
    default variables for depreciation calculations
    n = Economic life of the equipment -- default is 5 years
    p = Initial Investment -- default is $85,000
    s = Percent of innital value used to calculate salvage value
    --- default is 20% of p
        """
    n = 5.0
    p = 85000.00
    s = 0.2
    dbMultiplier = 2.0
    intPct = 0.12
    insPct = 0.03
    taxPct = 0.03

    @classmethod
    def AVI(cls, P, S, N):
        return (((P-S)*(N+1))/(2*N)) + S

    @classmethod
    def sVal(cls, arbitrary=None):
        if arbitrary is not None:
            return arbitrary
        else:
            return cls.s*cls.p

    @classmethod
    def depRate(cls):
        '''
        Depreciation Rate
        -----------------
        n: economic life in years
        '''
        return 1.0/cls.n

    @classmethod
    def depStraitLine(cls, sval=None):
        '''
        Strait line method
        ------------------
        p: innital investment cost of equipment
        s: salvage value
        n: economic life in years
        '''
        if sval is None:
            salvage = cls.sVal()
        else:
            salvage = cls.sVal(arbitrary=sval)
        return (cls.p-salvage)/cls.n

    @classmethod
    def depDecBalance(cls):
        '''Declining balance method'''
        sched = {}
        undepValue = cls.p
        annDep = 0
        for year in range(int(cls.n)):
            sched['year' + str(year)] = (annDep, undepValue)
            annDep = undepValue * (cls.depRate() * cls.dbMultiplier)
            undepValue = undepValue - annDep
        return sched

    @classmethod
    def depSOYD(cls, sval=None):
        '''Sum-of-years-digits method'''
        if sval is None:
            salvage = cls.sVal()
        else:
            salvage = cls.sVal(arbitrary=sval)
        sched = {}
        undepValue = cls.p
        tDep = cls.p - salvage
        annDep = 0
        sched['year0'] = (annDep, undepValue)
        years = range(1, int(cls.n) + 1)
        revyears = sorted(years, reverse=True)
        for y in range(len(years)):
            annDep = tDep * revyears[y]/sum(years)
            undepValue = undepValue - annDep
            sched['year' + str(years[y])] = (annDep, undepValue)
        return sched

# TODO: Need to add alternate method relevant to SOYD and decBalance methods
    @classmethod
    def ITT(cls, ann=False, depMeth=None):
        if ann is False:
            avi = AVI(cls.p, cls.sVal(), cls.n)
            interest = cls.intPct * avi
            insurance = cls.insPct * avi
            taxes = cls.taxPct * avi
            return interest + insurance + taxes


class MiyTime:
    '''default variables for time calculations
    SH = shceduled time
    H = productive time
    '''
    capFactor = 0.9
    hrsPerDay = 8
    daysPerWk = 5
    weeksPerYr = 52
    utRate = {"Chain saw-straight blade": 0.5,
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

    @classmethod
    def annWkDys(cls):
        return cls.daysPerWk*cls.weeksPerYr*cls.hrsPerDay

    @classmethod
    def SH(cls):
        return cls.capFactor * cls.annWorkDays

    @classmethod
    def H(cls, equipU='Grapple skidder'):
        return cls.SH * cls.utRate[equipU]

#    class opCost:
