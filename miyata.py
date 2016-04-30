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


# ## Depreciation
class DpAsset:
    """Calcultaing depreciation of an asset
    default variables for depreciation calculations
    n = Economic life of the equipment -- default is 5 years
    p = Initial Investment -- default is $85,000
    s = Percent of innital value used to calculate salvage value
    --- default is 20% of p
        """

    # Default Variables
    P = 85000.00
    N = 5.0
    sPct = 0.2
    mRatio = 1.1  # times annual depreciation

    # Fuel Density
    DieselLbGal = 7.08
    GasLbGal = 6.01

    # Fuel consumption
    fCosnHpHr = 0.4
    
    # Fuel Price
    fPriceDiesel = 2.614
    fPriceTax = 0.2429

    # Depreciation 
    dbMultiplier = 2.0

    # Interest insurance andf taxes
    intPct = 0.12
    insPct = 0.03
    taxPct = 0.03

    # Machine horsepower
    hp = 150
    # ratio of average net horsepower used
    # to average net horsepower available
    hpRatio = 0.65

    # Labor Costs
    wages = 15.82  # http://www.bls.gov/oes/current/oes454029.htm#(2)

    # Tires
    tireCost = 1000.00
    tireLife = 3000  # Hours

    # Lbs of engine oil consumed between
    # oil changed per horsepower hour
    eOilCons = 0.0006

    # Weight of engine oil (lbs/gallon)
    eOilWeight = 7.4

    # Percent of engine oil costs for other lubricants
    oLube = 0.5

    # Engine oil cost/gallon
    eOilCost = 4.00

    #Crank case capacity
    cCap = 5  # gallons

    #Time between crank case oil changes
    cTime = 90  # hrs
    
    @classmethod
    def AVI(cls):
        '''average value of yearly investment (AVI)'''
        return (((cls.P-cls.sVal())*(cls.N+1))/(2*cls.N)) + cls.S

    @classmethod
    def maintCost(cls, dep):
        '''
        Calculates annual maintenance costs based on
        dep = annual depreciation
        mRatio = percent of depreciation cost assumed for maintenance and,
        pTime = annual productive time
        '''
        return (dep*cls.mRatio)/cls.pTime

    @classmethod
    def gPerHr(cls):
        ''' Calculate fuel consumption in gallons/hr using:
        lbsHr = pounds / hp hr (FAO 1976)
        hpRatio = ratio of used to available horsepower
        hp = horsepower
        fDens = fuel density in lbs/gallon
        '''
        return ((cls.fCosnHpHr * cls.hpRatio)/cls.fDens)*cls.hp

    @classmethod
    def hrFuelCost(cls)
        '''
        calculates hourly fuel cost based upon:
        gHr = fuel consumption (gallons/hr)
        hp = horsepower
        price = fuel price ($/gallon)
        tax = fuel tax ($/gallon)
        '''
        return cls.gPerHr() * cls.hp * (cls.fPriceDiesel + cls.fPriceTax)

    @classmethod
    def Q(cls):
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
        return cls.hpRatio * ((cls.hpRatio * cls.eOilCons) / cls.eOilWeight) + (cls.cCap / cls.cTime)

    @classmethod
    def hourlyQ(cls, q, hp, price, c, t):
        return (cls.Q() * cls.hp + (cls.cCap/cls.cTime)) * (cls.fPriceDiesel + cls.fPriceTax)

    @classmethod
    def oLubeCost(hQ, otherL):
        return hQ * otherL

    @classmethod
    def hTireCost(tCost=tireCost, tLife=tireLife,  maintPct=0.15):
        """
        calculates hourly tire costData
        """
        return ((1+maintPct)*tCost)/tLife

    @classmethod
    def sVal(s=sPct, p=P, arbitrary=None):
        '''
        calculate salvage value as a percantage of P
        '''
        if arbitrary is not None:
            return arbitrary
        else:
            return sPct*p

        
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
            salvage = sVal()
        else:
            salvage = sVal(arbitrary=sval)
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
            salvage = sVal()
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
            avi = AVI(cls.p, sVal(), cls.n)
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
        return cls.capFactor * cls.annWkDys()

    @classmethod
    def H(cls, equipU='Grapple skidder'):
        return cls.SH() * cls.utRate[equipU]
