import pandas as pd
import os
import datetime
import sys

sys.path.append(os.getcwd())
from DataFunctions.DataReaders import MT5SymbolsDataReader

def NoLimitHitMapping(data, limit):
    """
    A function for the "No Limit Hit" mapping process.
    Iterates through the data and labels a trade at each bar if a trade can be made that isn't stopped out.
        -> "Can I make a trade that is profitable without being stopped out, and which direction is that trade?"
    Also adds the maximum PnL of the trade and the exit index.

    Parameters:
    data (pd.DataFrame): The OHLC dataframe of the data to map.
    limit (int or float): As specified limit to hold as a stop loss. Nb input in absolute values and not pips.

    Returns:
    data (pd.DataFrame): The original dataset with extra columns reflecting the mapping.
    """
    
    data['shortLossHit'] = [""] * len(data)
    data['maxShortPnL'] = [""] * len(data)
    data['shortExitIndex'] = [""] * len(data)

    data['longLossHit'] = [""] * len(data)
    data['maxLongPnL'] = [""] * len(data)
    data['longExitIndex'] = [""] * len(data)


    for i in range(1, len(data)-1):
        openPrice = data.loc[i, 'open']        
        
        #Long
        j = data.where(openPrice - data.loc[i+1:,'low'] >= limit).first_valid_index()
        data.loc[i, 'longLossHit'] = j
        maxPoint = data.loc[data.loc[i+1:j-1, 'high'].idxmax()]          
        data.loc[i,'maxLongPnL'] = maxPoint['high'] - openPrice
        data.loc[i,'longExitIndex'] = maxPoint.name

        #Short
        j = data.where(data.loc[i+1:,'high'] - openPrice >= limit).first_valid_index()
        data.loc[i, 'shortLossHit'] = j
        minPoint = data.loc[data.loc[i+1:j-1, 'low'].idxmin()]          
        data.loc[i,'maxShortPnL'] = minPoint['low'] - openPrice
        data.loc[i,'shortExitIndex'] = minPoint.name
            
        if i % (round(0.01 * len(data), 0)) == 0:
                print("Progress: {}% ".format(round(100 * (i/len(data)))), end = "\r", flush = True)            

    return data

data_filename = "EURUSD.a_M1_202009020000_202209022356.csv"
data_folder = os.path.join(os.getcwd() , 'Datasets', 'OHLC_Only')
data_dir = os.path.join(data_folder, data_filename)
data = MT5SymbolsDataReader(data_dir)

limit = 20/10000
mappedDat = NoLimitHitMapping(data, 20/10000)

print("Complete")