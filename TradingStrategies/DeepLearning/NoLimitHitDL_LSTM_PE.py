import pandas as pd 
import numpy as np
import ta
import os
import sys
pd.set_option('mode.chained_assignment', None)

sys.path.append(os.getcwd())
from TradingStrategies.DeepLearning.NoLimitHitDL import NoLimitHitDL
from TradingStrategies.DeepLearning.NoLimitHitDL_PE import NoLimitHitDL_PE
import tensorflow as tf
from keras.layers import Embedding
from keras.layers import Layer

class NoLimitHitDL_LSTM_PE(NoLimitHitDL_PE):
    def __init__(self, model, indicatorList):
        super().__init__(model, indicatorList)
        self.Name = model.layers[0].__class__.__name__ + "_PE_NoLimitHitDL"   
        #Need to adjust sequence length inference from model shape as this is based on the final deep model
        #Original sequence length should be input shape / features, so indicator list + 4 for OHLC
        self.sequence_length = int(self.model.input_shape[1])

    def reshape_sequence(self):
        self.input_sequence_scaled = tf.reshape(self.input_sequence_scaled, (self.input_sequence_scaled.shape[0], self.sequence_length, (len(self.indicatorList) + 4)))

    def run(self, data):
        self.add_data(data)
        self.clean_columns()
        self.add_indicator()       
        self.sequence_input()         
        self.scale_input()    
        self.encode_positions()    
        self.reshape_sequence()
        return self.determine_signal()

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