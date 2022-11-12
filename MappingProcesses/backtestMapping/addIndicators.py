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

    signalIdx = list(mappedDataWIndicators.columns).index('signal')
    firstCols = list(mappedDataWIndicators.columns)[:signalIdx]
    endCols = list(mappedDataWIndicators.columns)[signalIdx:]
    colsOrder = firstCols + indicatorList + endCols

    if 'CCI' in indicatorList:
        mappedDataWIndicators['CCI'] = ta.trend.CCIIndicator(mappedDataWIndicators['high'], mappedDataWIndicators['low'], mappedDataWIndicators['close'], window = 14).cci()

    if 'pSAR' in indicatorList:
        mappedDataWIndicators['pSAR'] = ta.trend.PSARIndicator(high = mappedDataWIndicators['high'], low = mappedDataWIndicators['low'], close = mappedDataWIndicators['close'], step = 0.02, max_step = 0.2).psar()

    if 'DC' in indicatorList:
        mappedDataWIndicators['D_UC'], mappedDataWIndicators['D_LC'] = [0] * len(mappedDataWIndicators), [0] * len(mappedDataWIndicators)
        DC_periods = 20
        for i in range(DC_periods, len(mappedDataWIndicators)):
            mappedDataWIndicators['D_UC'].iloc[i-1] = max(mappedDataWIndicators['high'].iloc[i-DC_periods:i])
            mappedDataWIndicators['D_LC'].iloc[i-1] = min(mappedDataWIndicators['low'].iloc[i-DC_periods:i])

    if 'BB' in indicatorList:
        mappedDataWIndicators['BBHigh'] = ta.volatility.BollingerBands(mappedDataWIndicators['close']).bollinger_hband()
        mappedDataWIndicators['BBLow'] = ta.volatility.BollingerBands(mappedDataWIndicators['close']).bollinger_lband()           

    mappedDataWIndicators = mappedDataWIndicators[~mappedDataWIndicators[indicatorList].isna().any(axis = 1)].reset_index(drop = True)
    mappedDataWIndicators = mappedDataWIndicators[colsOrder]

    return mappedDataWIndicators


data_folder = os.path.join(os.getcwd(), "MappingProcesses", "backtestMapping", "MappedDatasets")
data_filename = "CCI_301022-123427_EURUSD.a_M5__2017-09-04_to_2021-09-03_15Limit_Mapped.csv"
data_dir = os.path.join(data_folder, data_filename)

mappedData = pd.read_csv(data_dir)

indicatorList = ['pSAR']

mappedDataWIndicators = addIndicators(mappedData, indicatorList)

export_folder = os.path.join(os.getcwd(), "MappingProcesses", "backtestMapping", "MappedDatasets", "ExtraIndicators")
export_filename = data_folder.split("\\")[-1] + "_MappedWIndicators.csv"

export_dir = os.path.join(export_folder, export_filename)
mappedDataWIndicators.to_csv(export_dir, index = False)
print("Exported")