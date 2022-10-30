import pandas as pd 
import numpy as np

class PredictiveDL:
    def __init__(self, model):
        self.model = model
        self.sequence_length = self.model.input_shape[1]

    def add_data(self, data):
        self.data = data

    def clean_columns(self):
        self.data = self.data[['time', 'open', 'high', 'low', 'close']]
        self.InputData = self.data[['open', 'high', 'low', 'close']]

    def scale_input(self):
        
        #Row-wise Scaling
        rowMax = self.input_sequence.max(axis = 1)
        rowMin = self.input_sequence.min(axis = 1)
        self.input_sequence_scaled = (self.input_sequence - rowMin[:, np.newaxis]) / (rowMax[:, np.newaxis] - rowMin[:, np.newaxis])
        self.input_sequence_scaled = np.reshape(self.input_sequence_scaled, (1, self.input_sequence_scaled[-1].shape[0], self.input_sequence_scaled[-1].shape[1]))

    def sequence_input(self):
        #Using just one observation

        X = []
        X.append(self.InputData.iloc[-self.sequence_length:])
        X = np.array(X)

        self.input_sequence = X  
                    
    def determine_signal(self):

        action = 0

        prediction = self.model.predict(self.input_sequence, verbose = 0)
        prediction = prediction[0][0]

        if prediction > self.data['close'].iloc[-1]:
            action = 1
        elif prediction < self.data['close'].iloc[-1]:
            action = -1

        return action

    def run(self, data):
        self.add_data(data)
        self.clean_columns()
        self.sequence_input() 
        self.scale_input()        
        return self.determine_signal()