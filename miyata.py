import util as ut

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
    N = Economic life of the equipment -- default is 5 years
    P = Initial Investment -- default is $85,000
    sPct = Percent of innital value used to calculate salvage value
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
    tireRetread = 500.00
    tireLife = 3000  # Hours
    tireMpct = 0.15

    # Lbs of engine oil consumed between
    # oil changed per horsepower hour
    eOilCons = 0.0006

    # Weight of engine oil (lbs/gallon)
    eOilWeight = 7.4

    #Engine oil price
    oPrice = 400.0/55.0
    
    # Percent of engine oil costs for other lubricants
    oLube = 0.5

    # Engine oil cost/gallon
    eOilCost = 4.00

    # Crank case capacity
    cCap = 5  # gallons

    # Time between crank case oil changes
    cTime = 90  # hrs

    @classmethod
    def AVI(cls):
        '''average value of yearly investment (AVI)'''
        return (((cls.P-cls.sVal())*(cls.N+1))/(2*cls.N)) + cls.sVal()

    @classmethod
    def maintCost(cls, dep, SH):
        '''
        Calculates annual maintenance costs based on
        dep = annual depreciation
        mRatio = percent of depreciation cost assumed for maintenance and,
        pTime = annual productive time
        '''
        return (dep*cls.mRatio)/SH

    @classmethod
    def gPerHr(cls):
        ''' Calculate fuel consumption in gallons/hr using:
        lbsHr = pounds / hp hr (FAO 1976)
        hpRatio = ratio of used to available horsepower
        hp = horsepower
        fDens = fuel density in lbs/gallon
        '''
        return (cls.fCosnHpHr * cls.hpRatio)/cls.DieselLbGal

    @classmethod
    def hrFuelCost(cls):
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
    def hourlyQ(cls):
        return (cls.Q() * cls.hp + (cls.cCap/cls.cTime)) * (cls.oPrice + cls.fPriceTax)

    @classmethod
    def oLubeCost(cls):
        return cls.hourlyQ() * cls.oLube

    @classmethod
    def hTireCost(cls):
        """
        calculates hourly tire costData
        """
        return ((1+cls.tireMpct)*(cls.tireCost+cls.tireRetread))/cls.tireLife

    @classmethod
    def sVal(cls, arbitrary=None):
        '''
        calculate salvage value as a percantage of P
        '''
        if arbitrary is not None:
            return arbitrary
        else:
            return cls.sPct*cls.P

    @classmethod
    def depRate(cls):
        '''
        Depreciation Rate
        -----------------
        n: economic life in years
        '''
        return 1.0/cls.N

    @classmethod
    def depStraitLine(cls, sval=None):
        '''
        Strait line method
        ------------------
        '''
        if sval is None:
            salvage = cls.sVal()
        else:
            salvage = cls.sVal(arbitrary=sval)
        return (cls.P-salvage)/cls.N

    @classmethod
    def depDecBalance(cls):
        '''Declining balance method'''
        sched = {}
        undepValue = cls.P
        annDep = 0
        for year in range(int(cls.N)):
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
        undepValue = cls.P
        tDep = cls.P - salvage
        annDep = 0
        sched['year0'] = (annDep, undepValue)
        years = range(1, int(cls.N) + 1)
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
            avi = cls.AVI(cls.P, cls.sVal(), cls.N)
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
        '''Annual work days'''
        return cls.daysPerWk*cls.weeksPerYr*cls.hrsPerDay

    @classmethod
    def SH(cls):
        '''Scheduled time (SH)'''
        return cls.capFactor * cls.annWkDys()

    @classmethod
    def H(cls, equipU='Grapple skidder'):
        ''' Productive Time (H)'''
        if isinstance(equipU, float) is True:
            rate = equipU
        elif isinstance(equipU, str) is True:
            rate = cls.utRate[equipU]
        return cls.SH() * rate



    def fixedAnnual(dep, avi, iit, H):
    """Calculates fixed annual costs"""
    return {'Depreciation': dep,
            'Average vaule of yearly investment': avi,
            'Interest insurance and taxes': iit,
            'Fixed annual costs': dep + (avi * iit)}

fixedCosts = (DpAsset.depStraitLine() + DpAsset.AVI())/MiyTime.H()
maintenance = DpAsset.maintCost(DpAsset.depStraitLine(), MiyTime.H())
fuel = DpAsset.hrFuelCost()

oil = DpAsset.hourlyQ() + DpAsset.oLubeCost()
tires = DpAsset.hTireCost()
