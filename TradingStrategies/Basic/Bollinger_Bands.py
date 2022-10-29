import pandas as pd
import ta

class Bollinger_Bands:

    def __init__(self):
        
        self.Name = "BollingerBands"
        self.indicatorDf = None

    def addData(self, data):
        
        self.df = data
        self.open = self.df["open"]
        self.high = self.df["high"]
        self.low = self.df["low"]
        self.close = self.df["close"]

    def calculate_BB(self):
        self.df['BBHigh'] = ta.volatility.BollingerBands(self.df['close']).bollinger_hband()
        self.df['BBLow'] = ta.volatility.BollingerBands(self.df['close']).bollinger_lband()

    def determine_signal(self):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        high = self.df['high']
        low = self.df['low']
        BBHigh = self.df['BBHigh']
        BBLow = self.df['BBLow']

        #Buy Signal - high price touches high BB

        if high.iloc[-1] >= BBHigh.iloc[-1]:
            
            action = 1

        #Sell Signal - low price touches low BB

        if low.iloc[-1] <- BBLow.iloc[-1]:

            action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'BBHigh', 'BBLow']]

    def run(self, data):
        self.addData(data)
        self.calculate_BB()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf