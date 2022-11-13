import pandas as pd 
import numpy as np
import ta
pd.set_option('mode.chained_assignment', None)

class NoLimitHitDL:
    def __init__(self, model, indicatorList):
        self.model = model
        self.sequence_length = self.model.input_shape[1]
        self.indicatorList = indicatorList
        self.Name = model.layers[0].__class__.__name__ + "_NoLimitHitDL"
    
    def add_data(self, data):
        self.data = data

    def clean_columns(self):
        self.data = self.data[['time', 'open', 'high', 'low', 'close']]

    def sequence_input(self):        
        #Using just one observation

        X = []
        X.append(self.inputData.iloc[-self.sequence_length:])
        X = np.array(X)

        self.input_sequence = X  

    def add_indicator(self):
        #Add here given the possible combinations   

        if 'CCI' in self.indicatorList:
            self.data['CCI'] = ta.trend.CCIIndicator(self.data['high'], self.data['low'], self.data['close'], window = 14).cci()

        if 'pSAR' in self.indicatorList:
            self.data["pSAR"] = ta.trend.PSARIndicator(high = self.data['high'], low = self.data['low'], close = self.data['close'], step = 0.02, max_step = 0.2).psar()
            
            if 'pSARClose' in self.indicatorList:
                self.data['pSARClose'] = self.data['pSAR'] - self.data['close']

        if 'DC' in self.indicatorList:
            self.data['D_UC'], self.data['D_LC'] = [0] * len(self.data), [0] * len(self.data)
            DC_periods = 20
            for i in range(DC_periods, len(self.data)):
                self.data['D_UC'].iloc[i-1] = max(self.data['high'].iloc[i-DC_periods:i])
                self.data['D_LC'].iloc[i-1] = min(self.data['low'].iloc[i-DC_periods:i])

        if 'BB' in self.indicatorList:
            self.data['BBHigh'] = ta.volatility.BollingerBands(self.data['close']).bollinger_hband()
            self.data['BBLow'] = ta.volatility.BollingerBands(self.data['close']).bollinger_lband()    

            if 'HBBH' in self.indicatorList:
                self.data['HBBH'] = self.data['high'] - self.data['BBHigh']

            if 'LBBL' in self.indicatorList:
                self.data['LBBL'] = self.data['low'] - self.data['BBLow']

        if 'HO' in self.indicatorList:
            self.data['HO'] = self.data['high'] - self.data['close']

        if 'CL' in self.indicatorList:
            self.data['CL'] = self.data['close'] - self.data['low']

        self.inputData = self.data.drop(columns = 'time')

    def scale_input(self):
        
        #Row-wise Scaling
        rowMax = self.input_sequence.max(axis = 1)
        rowMin = self.input_sequence.min(axis = 1)
        self.input_sequence_scaled = (self.input_sequence - rowMin[:, np.newaxis]) / (rowMax[:, np.newaxis] - rowMin[:, np.newaxis])
        self.input_sequence_scaled = np.reshape(self.input_sequence_scaled, (1, self.input_sequence_scaled[-1].shape[0], self.input_sequence_scaled[-1].shape[1]))   
                    
    def determine_signal(self):

        action = 0

        prediction = self.model.predict(self.input_sequence_scaled)

        action = np.argmax(prediction, axis = 1) - 1

        return action[0]

    def run(self, data):        
        self.add_data(data)
        self.clean_columns()
        self.add_indicator()       
        self.sequence_input() 
        self.scale_input()        
        return self.determine_signal()