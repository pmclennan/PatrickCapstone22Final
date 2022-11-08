import pandas as pd
import os
import datetime
import sys

sys.path.append(os.getcwd())
from DataFunctions.DataReaders import MT5SymbolsDataReader

def NoLimitHitMapping(data, limit, numBars):
    """
    A function for the "No Limit Hit" mapping process.
    Iterates through the data and labels a trade at each bar if a trade can be made that isn't stopped out within the number of bars.
        -> "Can I make a trade that is profitable without being stopped out, and which direction is that trade?"
    Also adds the maximum PnL of the trade and the exit index.

    Parameters:
    data (pd.DataFrame): The OHLC dataframe of the data to map.
    limit (int or float): As specified limit to hold as a stop loss. Nb input in absolute values and not pips.

    Returns:
    data (pd.DataFrame): The original dataset with extra columns reflecting the mapping.
    """
    
    data['shortLossHit'] = [""] * len(data)
    data['maxShortPnL'] = [0] * len(data)
    data['shortExitIndex'] = [""] * len(data)

    data['longLossHit'] = [""] * len(data)
    data['maxLongPnL'] = [0] * len(data)
    data['longExitIndex'] = [""] * len(data)

    data['Signal'] = [0] * len(data)


    for i in range(1, len(data)-numBars-1):
        openPrice = data.loc[i, 'open']        
        
        #Long
        j = data.where(openPrice - data.loc[i+1:numBars+1,'close'] >= limit).first_valid_index()
        if j is not None and j - i > 1:
            data.loc[i, 'longLossHit'] = j

        elif j is None:
            j = i + numBars + 1

        maxPoint = data.loc[data.loc[i+1:j-1, 'close'].idxmax()]

        if maxPoint['close'] > openPrice:
            data.loc[i,'maxLongPnL'] = maxPoint['close'] - openPrice
            data.loc[i,'longExitIndex'] = maxPoint.name

        #Short
        j = data.where(data.loc[i+1:numBars+1,'close'] - openPrice >= limit).first_valid_index()
        if j is not None and j - i > 1:
            data.loc[i, 'shortLossHit'] = j

        elif j is None:
            j = i + numBars + 1
            
        minPoint = data.loc[data.loc[i+1:j-1, 'close'].idxmin()]          
        
        if minPoint['close'] < openPrice:
            data.loc[i,'maxShortPnL'] = openPrice - minPoint['close']
            data.loc[i,'shortExitIndex'] = minPoint.name
            
        ##Signal
        #Case where signal in both directions identified (unlikely)
        #Map to best trade (long if equal)
        if (data.loc[i, 'maxLongPnL'] != 0) and (data.loc[i, 'maxShortPnL'] != 0):
            if (data.loc[i, 'maxLongPnL'] >= data.loc[i, 'maxShortPnL']):
                data.loc[i, 'Signal'] = 1
            else:
                data.loc[i, 'Signal'] = -1
            
        #Case where long trade identified
        elif (data.loc[i, 'maxLongPnL'] != 0) and (data.loc[i, 'maxShortPnL'] == 0):
            data.loc[i, 'Signal'] = 1

        #Case where short trade identified
        elif (data.loc[i, 'maxShortPnL'] != 0) and (data.loc[i, 'maxLongPnL'] == 0):
            data.loc[i, 'Signal'] = -1

        if i % (round(0.01 * len(data), 0)) == 0:
                print("Progress: {}% ".format(round(100 * (i/len(data)))), end = "\r", flush = True)
        
    print("Progess: 100%")

    return data

data_folder = os.path.join(os.getcwd() , 'Datasets', 'OHLC_Only')
data_filename = "EURUSD.a_M5_201709040000_202109031210.csv"
data_dir = os.path.join(data_folder, data_filename)
data = MT5SymbolsDataReader(data_dir)

data = data.iloc

limit = 20/10000
numBars = 200
mappedDat = NoLimitHitMapping(data, limit, numBars)

exportDir = os.path.join(os.getcwd(), "MappingProcesses", "NoLimitHitMapping", "MappedDatasets")

mappedDat.to_csv(exportDir, index = False)

print("Complete")