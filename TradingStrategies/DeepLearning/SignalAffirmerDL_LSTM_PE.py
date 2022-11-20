import pandas as pd 
import numpy as np
import ta
import os
import sys
pd.set_option('mode.chained_assignment', None)

sys.path.append(os.getcwd())
from TradingStrategies.DeepLearning.SignalAffirmerDL import SignalAffirmerDL
from TradingStrategies.DeepLearning.SignalAffirmerDL_PE import SignalAffirmerDL_PE
import tensorflow as tf
from keras.layers import Embedding
from keras.layers import Layer

class SignalAffirmerDL_LSTM_PE(SignalAffirmerDL_PE):
    def __init__(self, model, indicatorStrategy, indicatorList = None):
        super().__init__(model, indicatorStrategy, indicatorList)
        self.Name = model.layers[0].__class__.__name__ + "_" + indicatorStrategy().Name + "_PE_SignalAffirmerDL"   
        #Need to adjust sequence length inference from model shape as this is based on the final deep model
        #Original sequence length should be input shape / features, so indicator list + 4 for OHLC
        self.sequence_length = int(self.model.input_shape[1])
        self.numFeatures = int(self.model.input_shape[2])

    def reshape_sequence(self):
        self.input_sequence_scaled = tf.reshape(self.input_sequence_scaled, (self.input_sequence_scaled.shape[0], self.sequence_length, self.numFeatures))

    def run(self, data):        
        self.add_data(data)
        self.clean_columns()
        self.run_indicator()

        if self.indicatorSignal != 0:
            self.add_indicator()
            
            if self.indicatorList is not None:
                self.add_extra_indicators()
            
            self.sequence_input()
            self.scale_input()
            self.encode_positions()    
            self.reshape_sequence()
            signal = self.determine_signal()
        else:
            signal = 0
        return signal

class PositionEmbeddingLayer(Layer):
    def __init__(self, sequence_length, output_dim, nFeatures, **kwargs):
        super(PositionEmbeddingLayer, self).__init__(**kwargs)
        self.position_embedding_layer = Embedding(
            input_dim=sequence_length, output_dim=output_dim
        )
        self.nFeatures = nFeatures
 
    def call(self, inputs):        
        position_indices = tf.range(tf.shape(inputs)[-2])
        embedded_indices = self.position_embedding_layer(position_indices)
        embedded_matrix = tf.repeat(embedded_indices, self.nFeatures, 1)
        return embedded_matrix