import pandas as pd
import ta

class Parabolic_SAR:
    def __init__(self):

        self.Name = 'pSAR'
        self.indicatorDf = None

    def addData(self, data):
        
        self.df = data
    
    def calculate_pSAR(self):
        self.df["pSAR"] = ta.trend.PSARIndicator(high = self.df['high'], low = self.df['low'], close = self.df['close'], step = 0.02, max_step = 0.2).psar()        

    def determine_signal(self):

        action = 0
        pSAR = self.df['pSAR']
        close = self.df['close']

        #Sell Criteria - current pSAR above close, previous pSAR below close
        if pSAR.iloc[-1] > close.iloc[-1] and pSAR.iloc[-2] < close.iloc[-2]:
            action = -1

        #Buy Criteria - current pSAR below close, previous pSAR above close
        elif pSAR.iloc[-1] < close.iloc[-1] and pSAR.iloc[-2] > close.iloc[-2]:
            action = 1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'pSAR']]

    def run(self, data):
        self.addData(data)
        self.calculate_pSAR()
        self.addIndicatorDf()
        
        return self.determine_signal(), self.indicatorDf