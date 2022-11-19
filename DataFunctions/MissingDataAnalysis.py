import pandas as pd
import os
from DataReaders import MT5SymbolsDataReader

def MissingDataAnalysis(dataset, frequency, print_output = False):
    
  dataset['time'] = pd.to_datetime(dataset['time'])
  
  dataset['Time Difference'] = dataset['time'].diff(1)
  
  comparison_table = dataset.groupby('Time Difference', as_index = False)['time'].nunique()
  comparison_table = comparison_table.rename(columns = {'time' : '# Occurrences'})
  comparison_table['% Data'] = round(comparison_table['# Occurrences']/len(dataset[1:]) * 100, 6)

  comparison_table = pd.DataFrame(comparison_table.sort_values(by = '# Occurrences', ascending = False)).reset_index(drop = True)
  comparison_table['# Frequency Deviations'] = round(comparison_table['Time Difference']/frequency, 2)

  comparison_table = comparison_table[['Time Difference', '# Frequency Deviations', '# Occurrences', '% Data']]
  comparison_table = comparison_table.sort_values(by = 'Time Difference', ignore_index = True)

  if print_output == True:
    print(comparison_table)
  return (comparison_table)

parentDir = os.path.join(os.getcwd(), 'Datasets')
subfolders = ['OHLC_Only', 'OHLC_BidAsk']
exportFolder = os.path.join(parentDir, 'MissingDataAnalysis')

for subfolder in subfolders:
    subDir = os.path.join(parentDir, subfolder)
    for root, dirs, files in os.walk(subDir):
        datasetType = root.split("\\")[-1]
        for file in files:
            fileDir = os.path.join(subDir, file)
            freq = file.split('EURUSD.a_')[1].split("_")[0]

            if freq == 'M1':
                freqDt = pd.Timedelta(1, 'm')
            elif freq == 'M5':
                freqDt = pd.Timedelta(5, 'm')

            if datasetType == 'OHLC_Only':
                dataset = MT5SymbolsDataReader(fileDir)
            else:
                dataset = pd.read_csv(fileDir)
                dataset.rename(columns = {'DATETIME': 'time'}, inplace = True)

            #MDA = MissingDataAnalysis(dataset, freqDt)

            summaryName = freq + "_" + datasetType

            if datasetType == 'OHLC_BidAsk':
                startDate = pd.to_datetime(dataset[dataset.columns[0]].iloc[0]).strftime('%d-%m-%Y')
                endDate = pd.to_datetime(dataset[dataset.columns[0]].iloc[-1]).strftime('%d-%m-%Y')
            else:
                startDate = dataset[dataset.columns[0]].iloc[0].strftime('%d-%m-%Y')
                endDate = dataset[dataset.columns[0]].iloc[-1].strftime('%d-%m-%Y')

            print(summaryName + " Length: ", len(dataset))
            print(summaryName + " Start Date: ", startDate)
            print(summaryName + " End Date: ", endDate)
            print("-------------------------------\n")

            
            #exportName = "MissingDataAnalysis_" + freq + "_" + datasetType + ".csv"
            #exportDir = os.path.join(exportFolder, exportName)
            #MDA.to_csv(exportDir, index = False)
            #print("Exported " + exportName)