import pandas as pd
import os
import datetime
import sys
import ta
pd.set_option('mode.chained_assignment', None)

sys.path.append(os.getcwd())
from DataFunctions.DataReaders import MT5SymbolsDataReader

def NoLimitHitMapping(data, limit, numBars, minPnL = 0.0001):

    """
    A function for the "No Limit Hit" mapping process.
    Iterates through the data and labels a trade at each bar if a trade can be made that isn't stopped out within the number of bars.
        -> "Can I make a trade that is profitable without being stopped out, and which direction is that trade?"
    Also adds the maximum PnL of the trade and the exit index.

    Parameters:
    data (pd.DataFrame): The OHLC dataframe of the data to map.
    limit (float): A specified limit to hold as a stop loss. Nb input in absolute values and not pips.
    numBars (int): The specified number of bars to look for the trade. 
    minPnL (float = 0.0001): A specified minimum PnL level. Will not map trades below this. Set as a proxy 0 by default.

    Returns:
    data (pd.DataFrame): The original dataset with extra columns reflecting the mapping.
    """    
    
    data['shortLossHit'] = [""] * len(data)
    data['maxShortPnL'] = [""] * len(data)
    data['shortExitIndex'] = [""] * len(data)

    data['longLossHit'] = [""] * len(data)
    data['maxLongPnL'] = [""] * len(data)
    data['longExitIndex'] = [""] * len(data)

    data['BestTradePnL'] = [""] * len(data)

    data['Signal'] = [0] * len(data)

    for i in range(len(data)-1):
        openPrice = data.loc[i+1, 'open']        

        #Long
        for j in range(i+2, min(len(data), i+2+numBars)):
            if openPrice - data.loc[j, 'close'] >= limit:
                if not data.loc[i+2:j].loc[data.loc[i+2:j, 'close'] - openPrice > minPnL].empty:
                    data.loc[i, 'longLossHit'] = j
                    maxPoint = data.loc[data.loc[i+2:j, 'close'].idxmax()]          
                    data.loc[i,'maxLongPnL'] = maxPoint['close'] - openPrice
                    data.loc[i,'longExitIndex'] = maxPoint.name                    
                break
            if j == min(len(data), i+2+numBars)-1 and not data.loc[i+2:j].loc[data.loc[i+2:j, 'close'] - openPrice > minPnL].empty:
                maxPoint = data.loc[data.loc[i+2:j, 'close'].idxmax()]          
                data.loc[i,'maxLongPnL'] = maxPoint['close'] - openPrice
                data.loc[i,'longExitIndex'] = maxPoint.name

        
        #Short
        for j in range(i+2, min(len(data), i+2+numBars)):
            if data.loc[j, 'close'] - openPrice >= limit:
                if not data.loc[i+2:j].loc[openPrice - data.loc[i+2:j, 'close']  > minPnL].empty:
                    data.loc[i, 'shortLossHit'] = j
                    minPoint = data.loc[data.loc[i+2:j, 'close'].idxmin()]          
                    data.loc[i,'maxShortPnL'] = openPrice - minPoint['close']
                    data.loc[i,'shortExitIndex'] = minPoint.name
                break
            if j == min(len(data), i+2+numBars)-1 and not data.loc[i+2:j].loc[openPrice - data.loc[i+2:j, 'close']  > minPnL].empty:
                minPoint = data.loc[data.loc[i+2:j, 'close'].idxmin()]          
                data.loc[i,'maxShortPnL'] = openPrice - minPoint['close']
                data.loc[i,'shortExitIndex'] = minPoint.name

        if data['maxLongPnL'].iloc[i] != "" and data['maxShortPnL'].iloc[i] == "":
            data['Signal'].iloc[i] = 1
            data['BestTradePnL'].iloc[i] = data['maxLongPnL'].iloc[i]

        elif data['maxShortPnL'].iloc[i] != "" and data['maxLongPnL'].iloc[i] == "":
            data['Signal'].iloc[i] = -1
            data['BestTradePnL'].iloc[i] = data['maxShortPnL'].iloc[i]

        elif data['maxShortPnL'].iloc[i] != "" and data['maxLongPnL'].iloc[i] != "":
            
            if data['maxLongPnL'].iloc[i] >= data['maxShortPnL'].iloc[i]:
                data['Signal'].iloc[i] = 1
                data['BestTradePnL'].iloc[i] = data['maxLongPnL'].iloc[i]
            
            elif data['maxLongPnL'].iloc[i] < data['maxShortPnL'].iloc[i]:
                data['Signal'].iloc[i] = -1
                data['BestTradePnL'].iloc[i] = data['maxShortPnL'].iloc[i]                
            
        if i % (round(0.01 * len(data), 0)) == 0:
            print("Mapping Progress: {}%".format(round(i/len(data) * 100)), end = "\r")

    print("Mapping Progress: 100%")
        
    return data

data_folder = os.path.join(os.getcwd() , 'Datasets', 'OHLC_Only')
data_filename = "EURUSD.a_M5_201709040000_202109031210.csv"
data_dir = os.path.join(data_folder, data_filename)
data = MT5SymbolsDataReader(data_dir)

limit = 20/10000
numBars = 200
mappedDat = NoLimitHitMapping(data, limit, numBars)

##Add indicators for features - top from backtests; CCI, pSAR, DC (combined with CCI) and Bollinger Bands
print("Adding CCI")
mappedDat['CCI'] = ta.trend.CCIIndicator(mappedDat['high'], mappedDat['low'], mappedDat['close'], window = 14).cci()

print("Adding pSAR")
mappedDat["pSAR"] = ta.trend.PSARIndicator(high = mappedDat['high'], low = mappedDat['low'], close = mappedDat['close'], step = 0.02, max_step = 0.2).psar()

print("Adding DC")
mappedDat['D_UC'], mappedDat['D_LC'] = [0] * len(mappedDat), [0] * len(mappedDat)
DC_periods = 20
for i in range(DC_periods, len(mappedDat)):
    mappedDat['D_UC'].iloc[i-1] = max(mappedDat['high'].iloc[i-DC_periods:i])
    mappedDat['D_LC'].iloc[i-1] = min(mappedDat['low'].iloc[i-DC_periods:i])

print("Adding BB")
mappedDat['BBHigh'] = ta.volatility.BollingerBands(mappedDat['close']).bollinger_hband()
mappedDat['BBLow'] = ta.volatility.BollingerBands(mappedDat['close']).bollinger_lband()

#Clean NAs from Indicators
mappedDat = mappedDat[~mappedDat.isna().any(axis = 1)].reset_index(drop = True)
exportName = data_filename.split(".csv")[0] + "NLH20_200.csv"
exportDir = os.path.join(os.getcwd(), "MappingProcesses", "NoLimitHitMapping", "MappedDatasets", exportName)

mappedDat.to_csv(exportDir, index = False)

print("Complete")