import pandas as pd
import os
import ta

def addIndicators(mappedData, indicatorList):

    """
    A function which adds other indicators to backtestMapping result for extra features in learning
    
    Parameters:
    mappedData (pd.DataFrame): Mapped dataset from backtestMapping
    indicatorList (list(str)): List of indicators to add. Cases outlied in the function

    Returns
    mappedDataWIndicators (pd.DataFrame): A dataframe of the mapped data with extra indicators added.
    """    

    mappedDataWIndicators = mappedData.copy()

    if 'CCI' in indicatorList:
        mappedDataWIndicators['CCI'] = ta.trend.CCIIndicator(mappedDataWIndicators['high'], mappedDataWIndicators['low'], mappedDataWIndicators['close'], window = 14).cci()

    if 'pSAR' in indicatorList:
        mappedDataWIndicators['pSAR'] = ta.trend.PSARIndicator(high = mappedDataWIndicators['high'], low = mappedDataWIndicators['low'], close = mappedDataWIndicators['close'], step = 0.02, max_step = 0.2).psar()

    if 'D_UC' in indicatorList:
        mappedDataWIndicators['D_UC'] = [0] * len(mappedDataWIndicators)         
        DC_periods = 20
        for i in range(DC_periods, len(mappedDataWIndicators)):
            mappedDataWIndicators['D_UC'].iloc[i-1] = max(mappedDataWIndicators['high'].iloc[i-DC_periods:i])
            
    if 'D_LC' in indicatorList:       
        mappedDataWIndicators['D_LC'] = [0] * len(mappedDataWIndicators)
        DC_periods = 20
        for i in range(DC_periods, len(mappedDataWIndicators)):
            mappedDataWIndicators['D_LC'].iloc[i-1] = min(mappedDataWIndicators['low'].iloc[i-DC_periods:i])

    if 'BBHigh' in indicatorList:
        mappedDataWIndicators['BBHigh'] = ta.volatility.BollingerBands(mappedDataWIndicators['close']).bollinger_hband()

    if 'BBLow' in indicatorList:        
        mappedDataWIndicators['BBLow'] = ta.volatility.BollingerBands(mappedDataWIndicators['close']).bollinger_lband()       

    if 'RSI' in indicatorList:
        mappedDataWIndicators['RSI'] = ta.momentum.RSIIndicator(mappedDataWIndicators['close']).rsi()

    mappedDataWIndicators = mappedDataWIndicators[~mappedDataWIndicators[indicatorList].isna().any(axis = 1)].reset_index(drop = True)

    return mappedDataWIndicators


data_folder = os.path.join(os.getcwd(), "MappingProcesses", "NoLimitHitMapping", "MappedDatasets")
data_filename = "EURUSD.a_M5_201709040000_202109031210NLH10SL_100Bars.csv"
data_dir = os.path.join(data_folder, data_filename)

mappedData = pd.read_csv(data_dir, index_col = [0])

indicatorList = ['RSI']

mappedDataWIndicators = addIndicators(mappedData, indicatorList)

export_folder = os.path.join(os.getcwd(), "MappingProcesses", "NoLimitHitMapping", "MappedDatasets", "ExtraIndicators")
export_filename = data_filename.split(".csv")[0] + "_MappedWIndicators2.csv"

export_dir = os.path.join(export_folder, export_filename)
mappedDataWIndicators.to_csv(export_dir, index = True)
print("Exported")