
import pandas as pd
import ta
import numpy as np
import os
import sys
sys.path.append(os.getcwd())
from TradingStrategies.IndicatorFunctions.StochasticOscilator import StochasticOscilator

class MACDStochasticCrossover:
    def __init__(self):
        
        self.Name = "MACD_SCO"
        self.indicatorDf = None

    def addData(self, data):
        self.df = data        
        
        self.close = self.df['close']
        self.high = self.df['high']
        self.low = self.df['low']

        self.df['macd_line'] = [0] * len(data)
        self.df['macd_signal'] = [0] * len(data)
        self.df['stoch_line'] = [0] * len(data)
        self.df['stoch_signal'] = [0] * len(data)
    
    def calculate_MACD(self):
        self.df['macd_line'] = ta.trend.MACD(close=self.close).macd()
        self.df['macd_signal'] = ta.trend.MACD(close=self.close).macd_signal()

    def calculate_SO(self):
        self.df["slow_k"], self.df["slow_d"] = StochasticOscilator(self.df, K = 14, D = 3, slowing = 3)   

    def determine_signal(self):
        m_line = self.df['macd_line']
        m_signal = self.df['macd_signal']
        k_line = self.df['slow_k']
        d_signal = self.df['slow_d']

        action = 0

        # SELL CRITERIA: stoch %k and %d lines crossover that are >80 shortly before MACD signal and line crossover that are >0
        if (k_line.iloc[-3] > 80 and d_signal.iloc[-3] > 80 and k_line.iloc[-2] > 80 and d_signal.iloc[
            -2] > 80) and \
                ((k_line.iloc[-3] < d_signal.iloc[-3] and k_line.iloc[-2] > d_signal.iloc[-2])) and \
                (m_line.iloc[-2] > 0 and m_signal.iloc[-2] > 0 and m_line.iloc[-1] > 0 and m_signal.iloc[
                    -1] > 0) and \
                (m_line.iloc[-2] > m_signal.iloc[-2] and m_line.iloc[-1] < m_signal.iloc[-1]):

            action = -1

        # BUY CRITERIA: stoch %k and %d lines crossover that are <20 shortly before MACD signal and line crossover that are <0
        elif (k_line.iloc[-3] < 20 and d_signal.iloc[-3] < 20 and k_line.iloc[-2] < 20 and d_signal.iloc[
            -2] < 20) and \
                ((k_line.iloc[-3] > d_signal.iloc[-3] and k_line.iloc[-2] < d_signal.iloc[-2])) and \
                (m_line.iloc[-2] < 0 and m_signal.iloc[-2] < 0 and m_line.iloc[-1] < 0 and m_signal.iloc[
                    -1] < 0) and \
                (m_line.iloc[-2] < m_signal.iloc[-2] and m_line.iloc[-1] > m_signal.iloc[-1]):

            action = 1

        return action

    def addIndicatorDf(self):
        self.indicatorDf = self.df[['time', 'macd_line', 'macd_signal', 'slow_k', 'slow_d']]

    def run(self, data):
        self.addData(data)
        self.calculate_MACD()
        self.calculate_SO()
        self.addIndicatorDf()
        return self.determine_signal(), self.indicatorDf