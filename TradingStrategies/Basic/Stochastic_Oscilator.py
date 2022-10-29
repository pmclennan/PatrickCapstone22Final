import pandas as pd
import ta
from TradingStrategies.IndicatorFunctions.StochasticOscilator import StochasticOscilator

class Stochastic_Oscilator:

    def __init__(self):
        
        self.Name = "StochasticOscilator"
        self.indicatorDf = None

    def addData(self, data):
        
        self.df = data

    def calculate_SO(self):
        self.df['slow_k'], self.df['slow_d'] = StochasticOscilator(self.df, K = 14, D = 3, slowing = 3)        

    def determine_signal(self):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        slow_k = self.df['slow_k']
        slow_d = self.df['slow_d']

        #Buy Signal - slow k or slow d goes below 20
        if slow_k.iloc[-1] < 20 or slow_d.iloc[-1] < 20:
            action = 1

        #Sell Signal - slow k or slow d goes above 80
        if slow_k.iloc[-1] > 80 or slow_d.iloc[-1] > 80:
            action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'slow_k', 'slow_d']]

    def run(self, data):
        self.addData(data)
        self.calculate_SO()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf