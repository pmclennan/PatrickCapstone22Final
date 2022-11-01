import pandas as pd 
import numpy as np

class SignalAffirmerDL:
    def __init__(self, model, indicatorStrategy):
        self.model = model
        self.indicatorStrategyClass = indicatorStrategy
        self.sequence_length = self.model.input_shape[1]
        self.Name = model.layers[0].__class__.__name__ + "_" + indicatorStrategy().Name + "_SignalAffirmerDL"
    
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

    def scale_input(self):
        
        #Row-wise Scaling
        rowMax = self.input_sequence.max(axis = 1)
        rowMin = self.input_sequence.min(axis = 1)
        self.input_sequence_scaled = (self.input_sequence - rowMin[:, np.newaxis]) / (rowMax[:, np.newaxis] - rowMin[:, np.newaxis])
        self.input_sequence_scaled = np.reshape(self.input_sequence_scaled, (1, self.input_sequence_scaled[-1].shape[0], self.input_sequence_scaled[-1].shape[1]))        
                    
    def determine_signal(self):

        prediction = round(self.model.predict(self.input_sequence_scaled)[0][0])
        action = prediction * self.indicatorSignal

        return action

    def run(self, data):        
        self.add_data(data)
        self.clean_columns()
        self.run_indicator()

        if self.indicatorSignal != 0:
            self.add_indicator()
            self.sequence_input()
            self.scale_input()
            signal = self.determine_signal()
        else:
            signal = 0
        return signal