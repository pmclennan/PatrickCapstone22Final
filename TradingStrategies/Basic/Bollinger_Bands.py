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
        self.df['BBMid'] = ta.volatility.BollingerBands(self.df['close']).bollinger_mavg()
        self.df['BBLow'] = ta.volatility.BollingerBands(self.df['close']).bollinger_lband()
        self.df['BBRange'] = self.df['BBHigh'] - self.df['BBLow']
        self.df['BBRange5MA'] = self.df['BBRange'].rolling(5).mean()

    def determine_signal(self):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        high = self.df['high']
        low = self.df['low']
        BBHigh = self.df['BBHigh']
        BBLow = self.df['BBLow']
        BBRange = self.df['BBRange']
        BBRange5MA = self.df['BBRange5MA']

        #Buy Signal:
        # if high price touches high BB, and BBRange > BBRangeMA T-1 (breakout)
        # if low price touches low BB, and BBRange <= BBRangeMA T-1 (retractment)

        if (high.iloc[-1] >= BBHigh.iloc[-1] and BBRange.iloc[-1] > BBRange5MA.iloc[-2]) or \
            (low.iloc[-1] <= BBLow.iloc[-1] and BBRange.iloc[-1] <= BBRange5MA.iloc[-2]):
            
            action = 1

        #Sell Signal:
        # if low price touches low BB, and BBRange > BBRangeMA (breakout)
        # if high price touches high BB, and BBRange <= BBRangeMA (retractment)

        if (low.iloc[-1] <= BBLow.iloc[-1] and BBRange.iloc[-1] > BBRange5MA.iloc[-2]) or \
            (high.iloc[-1] >= BBHigh.iloc[-1] and BBRange.iloc[-1] <= BBRange5MA.iloc[-2]):

            action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'BBHigh', 'BBMid', 'BBLow', 'BBRange', 'BBRange5MA']]

    def run(self, data):
        self.addData(data)
        self.calculate_BB()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf