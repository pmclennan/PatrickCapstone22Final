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
        CrossoverIdx = np.where(MACrossover)[0][-1]

        #Strategy is based on a crossover occuring near where the price flips between the bollinger bands 
        #E.g. MA crossover, hits High BB shortly (at least two bars) after then sticks to Low BB (at least 2 bars) -> Short

        if len(self.df) - CrossoverIdx <= MA_BBGap and \
            ((len(self.df) - CrossoverIdx <= 1) or \
                (high.iloc[-1] >= BBHigh.iloc[-1]) or \
                    (low.iloc[-1] <= BBLow.iloc[-1])):
            
            for i in range(10):
                #Buy - Only look at this if hit a crossover or touching BB
                if (high.iloc[-1] >= BBHigh.iloc[-1]) or (len(self.df) - CrossoverIdx <= 1): 
                    #Now check is there is a pattern of 2 highs hitting high BB
                    if all(high.iloc[-i-2:len(high)-i] >= BBHigh.iloc[-i-2:len(BBHigh)-i]):
                        #And prior to that, 2 lows hitting low BB
                        for j in range(i+1, i+11):
                            if all(low.iloc[-j-2:-j] <= BBLow.iloc[-j-2:-j]): 

                                action = 1
                                break
                
                if action != 0:
                    break
            
                #Likewise for sell
                elif (low.iloc[-1] <= BBLow.iloc[-1]) or (len(self.df) - CrossoverIdx <= 1):
                    if all(low.iloc[-i-2:len(low)-i] <= BBLow.iloc[-i-2:len(BBLow)-i]):
                        for j in range(i+1, i+11):
                            if all(high.iloc[-j-2:-j] >= BBHigh.iloc[-j-2:-j]):

                                action = -1
                                break      
                    
                if action != 0:
                    break

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'LongMA', 'ShortMA', 'BBHigh', 'BBLow']]

    def run(self, data):
        self.addData(data)
        self.calculate_BB()
        self.calculate_MA()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf