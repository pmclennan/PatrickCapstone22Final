import pandas as pd
import os

def backtestMapping(historyData, tradeData):

    """
    A function to map trade decisions from a backtest for Deep Learning Input.
    This applies two types of mapping:
    1. CorrectSignal (0/1) - if the predicted signal was correct/a profitable trade.
    2. SignalMapping (-1/0/1) - maps based on what the correct trade would be, where the label defines correct direction.
        Long trade is profitable: 1.
        Short trade is profitable: -1.
        Long trade is not profitable: -1 (as we would expect the short trade to be profitable instead)
        Short trade is not profitable: 1 (as we would expect the long trade to be profitable instead)
    
    Parameters:
    historyData (pd.DataFrame): History data from a backtest.
    tradeData (pd.DataFrame): Trade summary data from a backtest.

    Returns
    mappingData (pd.DataFrame): A dataframe of OHLC history + trade decision and mapping.
    """    

    mappingData = historyData.drop(columns = ['action', 'position', 'P/L', 'Total profit', 'Executed price', 'Take Profit', 'Stop Loss'])
    
    tradeData['CorrectSignal'] = [0] * len(tradeData)
    tradeData['CorrectSignal'].loc[tradeData['Trade P/L'] > 0] = 1

    tradeData['SignalMapping'] = [0] * len(tradeData)
    #Profitable Longs as 1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'buy') & (tradeData['Trade P/L'] > 0)] = 1
    #Non-profitable longs as -1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'buy') & (tradeData['Trade P/L'] < 0)] = -1
    #Profitable shorts as -1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'short') & (tradeData['Trade P/L'] > 0)] = -1
    #Non profitable shorts as 1
    tradeData['SignalMapping'].loc[(tradeData['Trade Type'] == 'short') & (tradeData['Trade P/L'] < 0)] = 1

    tradeData.rename(columns = {'Trade Open Time': 'time'}, inplace = True)

    mappingData = mappingData.merge(tradeData[['time', 'Trade P/L', 'CorrectSignal', 'SignalMapping']], how = 'left', on = 'time')   
    mappingData['SignalMapping'].fillna(0, inplace = True)

    return mappingData

##parentFolder = os.path.join(os.getcwd(), 'BacktestResults')
parentFolder = "C:\\Users\\Patrick\\Documents\\UNI - USYD\\2022 - Capstone\\Final Repo\\Large Files - Final"

subFolder = os.path.join('M1_2017-2021', 'BasicIndicators', "BollingerBands_011122-062248_EURUSD.a_M1__2017-09-04_to_2021-09-03_15Limit")
data_folder = os.path.join(parentFolder, subFolder)
history_filename = "History.csv"
trade_filename = 'Trade_Summary.csv'
history_dir = os.path.join(data_folder, history_filename)
trade_dir = os.path.join(data_folder, trade_filename)

historyData = pd.read_csv(history_dir)
tradeData = pd.read_csv(trade_dir)

mappingData = backtestMapping(historyData, tradeData)

#export_folder = os.path.join(os.getcwd(), "MappingProcesses", "backtestMapping", "MappedDatasets")
export_folder = os.path.join(parentFolder, 'MappedDatasets')
export_filename = data_folder.split("\\")[-1] + "_Mapped.csv"
export_dir = os.path.join(export_folder, export_filename)

mappingData.to_csv(export_dir, index = False)
print("Exported")