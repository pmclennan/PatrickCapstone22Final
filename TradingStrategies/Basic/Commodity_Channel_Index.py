import pandas as pd
import ta

class Commodity_Channel_Index:

    def __init__(self):
        
        self.Name = "CCI"
        self.indicatorDf = None

    def addData(self, data):
        
        self.df = data

    def calculate_CCI(self):
        self.df['CCI'] = ta.trend.CCIIndicator(self.df['high'], self.df['low'], self.df['close'], window = 14).cci()

    def determine_signal(self):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        CCI = self.df['CCI']

        #Buy Signal - CCI crosses over above 100
        if CCI.iloc[-2] < 100 and CCI.iloc[-1] > 100:
            action = 1

        #Sell Signal - CCI crosses over below -100
        if CCI.iloc[-2] > -100 and CCI.iloc[-1] < -100:
            action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'CCI']]

    def run(self, data):
        self.addData(data)
        self.calculate_CCI()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf