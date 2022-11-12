import pandas as pd 
import numpy as np
import ta
pd.set_option('mode.chained_assignment', None)

class SignalAffirmerDL:
    def __init__(self, model, indicatorStrategy, extraIndicators = None):
        self.model = model
        self.indicatorStrategyClass = indicatorStrategy
        self.sequence_length = self.model.input_shape[1]
        self.extraIndicators = list(extraIndicators)
        if extraIndicators is None:
            self.Name = model.layers[0].__class__.__name__ + "_" + indicatorStrategy().Name + "_SignalAffirmerDL"
        else:
            extraIndicatorString = ("+").join(self.extraIndicators)
            self.Name = model.layers[0].__class__.__name__ + "_" + indicatorStrategy().Name + "+" + extraIndicatorString + "_SignalAffirmerDL"
    
    def add_data(self, data):
        self.data = data

    def clean_columns(self):
        self.data = self.data[['time', 'open', 'high', 'low', 'close']]

    def run_indicator(self):
        self.indicatorStrategy = self.indicatorStrategyClass()
        self.indicatorSignal, self.indicatorDf = self.indicatorStrategy.run(self.data) 

    def sequence_input(self):        
        #Using just one observation

        X = []
        X.append(self.inputData.iloc[-self.sequence_length:])
        X = np.array(X)

        self.input_sequence = X  

    def add_indicator(self):
        #Indicator strategy now adds indicators to DF naturally.
        self.inputData = self.data.drop(columns = 'time')
        self.inputData['Signal'] = [0] * (len(self.inputData)-1) + [self.indicatorSignal]

    def add_extra_indicators(self):

        if 'CCI' in self.extraIndicators:
            self.inputData['CCI'] = ta.trend.CCIIndicator(self.inputData['high'], self.inputData['low'], self.inputData['close'], window = 14).cci()

        if 'pSAR' in self.extraIndicators:
            self.inputData["pSAR"] = ta.trend.PSARIndicator(high = self.inputData['high'], low = self.inputData['low'], close = self.inputData['close'], step = 0.02, max_step = 0.2).psar()

        if 'DC' in self.extraIndicators:
            self.inputData['D_UC'], self.inputData['D_LC'] = [0] * len(self.inputData), [0] * len(self.inputData)
            DC_periods = 20
            for i in range(DC_periods, len(self.inputData)):
                self.inputData['D_UC'].iloc[i-1] = max(self.inputData['high'].iloc[i-DC_periods:i])
                self.inputData['D_LC'].iloc[i-1] = min(self.inputData['low'].iloc[i-DC_periods:i])

        if 'BB' in self.extraIndicators:
            self.inputData['BBHigh'] = ta.volatility.BollingerBands(self.inputData['close']).bollinger_hband()
            self.inputData['BBLow'] = ta.volatility.BollingerBands(self.inputData['close']).bollinger_lband()

        signalIdx = list(self.inputData.columns).index('Signal')
        firstCols = list(self.inputData.columns)[:signalIdx]
        endCols = [list(self.inputData.columns)[signalIdx]]
        colsOrder = firstCols + self.extraIndicators + endCols

        self.inputData = self.inputData[colsOrder]

    def scale_input(self):
        
        #Row-wise Scaling
        signalInd = self.input_sequence.shape[2]-1
        rowMax = self.input_sequence[:, :, 0:signalInd].max(axis = 1)
        rowMin = self.input_sequence[:, :, 0:signalInd].min(axis = 1)

        self.input_sequence_scaled = self.input_sequence
        self.input_sequence_scaled[:, :, 0:signalInd] = (self.input_sequence_scaled[:, :, 0:signalInd] - rowMin[:, np.newaxis]) / (rowMax[:, np.newaxis] - rowMin[:, np.newaxis])
        self.input_sequence_scaled = np.reshape(self.input_sequence_scaled, (1, self.input_sequence_scaled[-1].shape[0], self.input_sequence_scaled[-1].shape[1]))        
                    
    def determine_signal(self):

        prediction = round(self.model.predict(self.input_sequence_scaled, verbose = 0)[0][0])
        action = prediction * self.indicatorSignal

        return action

    def run(self, data):        
        self.add_data(data)
        self.clean_columns()
        self.run_indicator()

        if self.indicatorSignal != 0:
            self.add_indicator()
            
            if self.extraIndicators is not None:
                self.add_extra_indicators()
            
            self.sequence_input()
            self.scale_input()
            signal = self.determine_signal()
        else:
            signal = 0
        return signal