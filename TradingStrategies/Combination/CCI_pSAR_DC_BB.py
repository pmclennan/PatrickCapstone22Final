import pandas as pd
import ta
import numpy as np
pd.set_option('mode.chained_assignment', None)

class CCI_pSAR_DC_BB:
    def __init__(self, CCI_window = 20, DC_periods = 20, SMA_window = 7, crossover_lookback = 5):

        self.Name ="CCI_pSAR_DC_BB"

        self.CCI_window = CCI_window
        self.DC_periods = DC_periods
        self.SMA_window = SMA_window
        self.crossover_lookback = crossover_lookback
        self.indicatorDf = None

    def addData(self, data):
        self.df = data
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

        self.df['CCI'] = [0] * len(self.df)
        self.df['pSAR'] = [0] * len(self.df)
        self.df['D_UC'] = [0] * len(self.df)
        self.df['D_LC'] = [0] * len(self.df)
        self.df['BBHigh'] = [0] * len(self.df)
        self.df['BBLow'] = [0] * len(self.df)        

    def add_CCI(self):
        self.df['CCI'] = ta.trend.CCIIndicator(self.df['high'], self.df['low'], self.df['close'], window = self.CCI_window).cci()

    def add_pSAR(self):
        self.df["pSAR"] = ta.trend.PSARIndicator(high = self.df['high'], low = self.df['low'], close = self.df['close'], step = 0.02, max_step = 0.2).psar()        

    def add_DC(self):
        for i in range(self.DC_periods, len(self.df)):
            self.df['D_UC'].iloc[i] = max(self.df['high'].iloc[i-self.DC_periods+1:i+1])
            self.df['D_LC'].iloc[i] = min(self.df['low'].iloc[i-self.DC_periods+1:i+1])

    def add_BB(self):
        self.df['BBHigh'] = ta.volatility.BollingerBands(self.df['close']).bollinger_hband()
        self.df['BBLow'] = ta.volatility.BollingerBands(self.df['close']).bollinger_lband()

    def determine_signal(self):
        
        action = 0
        

        if self.df['CCI'].iloc[-2] < 100 and self.df['CCI'].iloc[-1] > 100 and \
            self.df['pSAR'].iloc[-2] > self.df['close'].iloc[-2] and self.df['pSAR'].iloc[-1] < self.df['close'].iloc[-1] and \
                self.df['high'].iloc[-1] >= self.df['D_UC'].iloc[-1] and \
                    self.df['high'].iloc[-1] >= self.df['BBHigh'].iloc[-1]:
                        action = 1


        if self.df['CCI'].iloc[-2] > -100 and self.df['CCI'].iloc[-1] < -100 and \
            self.df['pSAR'].iloc[-2] < self.df['close'].iloc[-2] and self.df['pSAR'].iloc[-1] > self.df['close'].iloc[-1] and \
                self.df['low'].iloc[-1] <= self.df['D_LC'].iloc[-1] and \
                    self.df['low'].iloc[-1] <= self.df['BBLow'].iloc[-1]:
                        action = -1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'CCI', 'D_UC', 'D_LC', 'D_MC', 'SMA']]

    def run(self, data):
        self.addData(data)
        self.add_CCI()
        self.add_DC()
        self.add_SMA()
        self.addIndicatorDf()
        
        return self.determine_signal(), self.indicatorDf