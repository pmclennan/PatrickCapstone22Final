import pandas as pd
import ta

class MACD_Crossover:

    def __init__(self):
        
        self.Name = "MACDCrossover"
        self.indicatorDf = None

    def addData(self, data):      

        self.df = data

    def calculate_MACD(self):
        self.df['macd_line'] = ta.trend.MACD(close=self.df['close']).macd()
        self.df['macd_signal'] = ta.trend.MACD(close=self.df['close']).macd_signal()

    def determine_signal(self):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        macd = self.df['macd_line']
        signal = self.df['macd_signal']

        # SELL CRITERIA: if MACD line has crossed signal line and both have been > 0 in the past 3 bars
        if (macd.iloc[-1] > 0 and signal.iloc[-1] > 0) and \
            (macd.iloc[-2] > 0 and signal.iloc[-2] > 0) and \
            (macd.iloc[-3] > 0 and signal.iloc[-3] > 0) and \
            ((macd.iloc[-2] < signal.iloc[-2] and macd.iloc[-1] > signal.iloc[-1]) or \
                (macd.iloc[-2] > signal.iloc[-2] and macd.iloc[-1] < signal.iloc[-1])):
            action = -1

        # BUY CRITERIA: if MACD line has crossed signal line and both have been < 0 in the past 3 bars
        if (macd.iloc[-1] < 0 and signal.iloc[-1] < 0) and \
            (macd.iloc[-2] < 0 and signal.iloc[-2] < 0) and \
            (macd.iloc[-3] < 0 and signal.iloc[-3] < 0) and \
            ((macd.iloc[-2] > signal.iloc[-2] and macd.iloc[-1] < signal.iloc[-1]) or \
                (macd.iloc[-2] < signal.iloc[-2] and macd.iloc[-1] > signal.iloc[-1])):
            action = 1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'macd_line', 'macd_signal']]

    def run(self, data):
        self.addData(data)
        self.calculate_MACD()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf