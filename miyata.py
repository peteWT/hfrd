import util as ut
costData =ut.gData(
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
        '''
        self.n = 5.0
        self.p = 85000.00
        self.s = 17000.00
        self.dbMultiplier = 2.0
        
    def depRate(self):
        '''
        Depreciation Rate
        -----------------
        n: economic life in years
        '''
        return 1.0/self.n
    
    def depStraitLine(self):
        '''
        Strait line method
        ------------------
        p: innital investment cost of equipment
        s: salvage value
        n: economic life in years
        '''
        return (self.p-self.s)/self.n

    def depDecBalance(self):
        sched = {}
        undepValue = self.p
        annDep = 0
        for year in range(int(self.n)):
            sched['year'+str(year)]=[annDep, undepValue]
            annDep = undepValue * (self.depRate() * self.dbMultiplier)
            undepValue = undepValue - annDep
      
        return sched

    def depSOYD(self):
        depRateYear = [float(i)/sum(range(int(self.n))) for i in range(int(self.n))]
        return depRateYear
