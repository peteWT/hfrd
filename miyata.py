import util as ut
from operator import sub

# TODO: Dollars adjusted for inflation

costData = ut.gData(
    '1TsHo2wyvzKYugiDudPHFJjtFS--5ZBcWNb2gGopteX4',
    1475511425)
constants = ut.gData(
    '1TsHo2wyvzKYugiDudPHFJjtFS--5ZBcWNb2gGopteX4',
    1199790733)
fedtx, ltx, freight, salv, life, sophr, ptime = [constants.iloc[i].to_dict() for i in range(len(constants))]

# Default Variables
P = 85000.00
N = 5.0
sPct = 0.2
mRatio = 1.1  # times annual depreciation
DieselLbGal = 7.08
GasLbGal = 6.01
fPriceDiesel = 2.614
fPriceTax = 0.2429

# ratio of average net horsepower used
# to average net horsepower available
hpRatio = 0.65

# Lbs of engine oil consumed between
# oil changed per horsepower hour
eOilCons = 0.0006

# Weight of engine oil (lbs/gallon)
eOilWeight = 7.4

# Percent of engine oil costs for other lubricants
oLube = 0.5

# Engine oil cost/gallon
eOilCost = 4.00


def AVI(P, S, N):
    '''average value of yearly investment (AVI)'''
    return (((P-S)*(N+1))/(2*N)) + S


def maintCost(dep, mRatio, pTime):
    '''
    Calculates annual maintenance costs based on
    dep = annual depreciation
    mRatio = percent of depreciation cost assumed for maintenance and,
    pTime = annual productive time
    '''
    return (dep*mRatio)/pTime


def gPerHr(lbsHr, hpRatio, hp, fDens):
    ''' Calculate fuel consumption in gallons/hr using:
    lbsHr = pounds / hr (FAO 1976)
    hpRatio = ratio of used to available horsepower
    hp = horsepower
    fDens = fuel density in lbs/gallon
    '''
    return ((lbsHr * hpRatio)/fDens)*hp


def hrFuelCost(gHr, hp, price, tax):
    '''
    calculates hourly fuel cost based upon:
    gHr = fuel consumption (gallons/hr)
    hp = horsepower
    price = fuel price ($/gallon)
    tax = fuel tax ($/gallon)
    '''
    return gHr * hp * (price + tax)


def Q(hp, hpRatio, cons, oilDens, c, t):
    '''
    calculate engine oil consumption (Q)
    based upon:
    hp = horsepower
    hpRatio = ratio of used to available horsepower
    cons = consumption of engin oil between changes/ hp-hour
    oilDens = density of engine oil
    c = crank case capacity
    t = number of hours between oil changes
    '''
    return hp * ((hpRatio * cons) / oilDens) + (c / t)


def hourlyQ(q, hp, price, c, t):
    return (q * hp + (c/t)) * price


def oLubeCost(hQ, otherL):
    return hQ * otherL

# TODO: Add tire cost

# ## Depreciation
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

