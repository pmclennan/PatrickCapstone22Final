import pandas as pd 
import numpy as np
import ta
import os
import sys
pd.set_option('mode.chained_assignment', None)

sys.path.append(os.getcwd())
from TradingStrategies.DeepLearning.NoLimitHitDL import NoLimitHitDL
import tensorflow as tf
from keras.layers import Embedding
from keras.layers import Layer

class NoLimitHitDL_PE(NoLimitHitDL):
    def __init__(self, model, indicatorList):
        super().__init__(model, indicatorList)
        self.Name = model.layers[0].__class__.__name__ + "_NoLimitHitDL_PE"   
        #Need to adjust sequence length inference from model shape as this is based on the final deep model
        #Original sequence length should be input shape / features, so indicator list + 4 for OHLC
        self.sequence_length = int(self.model.input_shape[1] / (len(indicatorList) + 4))

    def encode_positions(self):
        
        input_sequence_length = self.input_sequence_scaled.shape[1]
        n_features = self.input_sequence_scaled.shape[2]
        output_dim = 1
        embeddingLayer = PositionEmbeddingLayer(input_sequence_length, output_dim, n_features)
        embeddedLayerOutput = embeddingLayer(self.input_sequence_scaled)

        self.input_sequence_scaled = (embeddedLayerOutput + self.input_sequence_scaled)
        self.input_sequence_scaled = tf.reshape(self.input_sequence_scaled, (self.input_sequence_scaled.shape[0], self.input_sequence_scaled.shape[1] * self.input_sequence_scaled.shape[2]))

    def run(self, data):
        self.add_data(data)
        self.clean_columns()
        self.add_indicator()       
        self.sequence_input()         
        self.scale_input()    
        self.encode_positions()    
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