import pandas as pd
import ta
import numpy as np
pd.set_option('mode.chained_assignment', None)

class MA_BB:
    def __init__(self, LongMAPeriod = 200, ShortMAPeriod = 50, MA_BBGap = 30, BB_BBGap = 10):

        self.Name = "MA_BB"

        self.LongMAPeriod = LongMAPeriod
        self.ShortMAPeriod = ShortMAPeriod
        self.MA_BBGap = MA_BBGap
        self.BB_BBGap = BB_BBGap
        self.indicatorDf = None

    def addData(self, data):
        self.df = data

        self.df['LongMA'] = [0] * len(self.df)
        self.df['ShortMA'] = [0] * len(self.df)
        self.df['BBHigh'] = [0] * len(self.df)
        self.df['BBLow'] = [0] * len(self.df)
    
    def calculate_BB(self):
        self.df['BBHigh'] = ta.volatility.BollingerBands(self.df['close']).bollinger_hband()
        self.df['BBLow'] = ta.volatility.BollingerBands(self.df['close']).bollinger_lband()
    
    def calculate_MA(self):
        self.df['LongMA'] = self.df['close'].rolling(self.LongMAPeriod).mean()
        self.df['ShortMA'] = self.df['close'].rolling(self.ShortMAPeriod).mean()

    def determine_signal(self):
        
        action = 0
        high = self.df['high']
        low = self.df['low']
        BBHigh = self.df['BBHigh']
        BBLow = self.df['BBLow']
        LongMA = self.df['LongMA']
        ShortMA = self.df['ShortMA']
        MA_BBGap = self.MA_BBGap
        BB_BBGap = self.BB_BBGap
        MADiff = ShortMA - LongMA
        MACrossover = np.sign(MADiff).diff().ne(0)

        #Strategy is based on a crossover, hitting one side of the BB a few times then sticking to the other side
        #E.g. MA crossover, hits High BB shortly after then sticks to Low BB -> Short

        #Buy - Hit BBHigh, recently hit a crossover and hit BBLow between that
        if all(high.iloc[-2:] >= BBHigh.iloc[-2:]) and any(MACrossover.iloc[-MA_BBGap:-3]):
            CrossoverIdx = np.where(MACrossover)[0][-1]
            if any(low.iloc[max(len(self.df) - BB_BBGap-3, CrossoverIdx):-3] <= BBLow.iloc[max(len(self.df) - BB_BBGap-3, CrossoverIdx):-3]):
            
                action = 1


        #Sell - Hit BBLow, recently hit BBHigh and hit crossover before that
        elif all(low.iloc[-2:] <= BBLow.iloc[-2:]) and any(MACrossover.iloc[-MA_BBGap:-3]):
            CrossoverIdx = np.where(MACrossover)[0][-1]
            if any(high.iloc[max(len(self.df) - BB_BBGap-3, CrossoverIdx):-3] >= BBHigh.iloc[max(len(self.df) - BB_BBGap-3, CrossoverIdx):-3]):
            
                action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'LongMA', 'ShortMA', 'BBHigh', 'BBLow']]

    def run(self, data):
        self.addData(data)
        self.calculate_BB()
        self.calculate_MA()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf