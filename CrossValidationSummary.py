import os
import sys
import pandas as pd

parentDir = os.path.join(os.getcwd(), "DLModels", "IndicatorMapping", "SignalAffirmerModels", "M5_CCI", "ParameterTuning")

colNames = ['Model', 'ParamSet', 'Param', 'Test Loss', 'Test Accuracy', 'Test Precision', 'Test Recall', \
    'Incorrect Trade Reduction (%)', 'Correct Trade Reduction (%)', 'Time Trained (s)']

summaryDF = pd.DataFrame(columns = colNames)

models = ['RNN', 'LSTM', 'GRU']

for root, dirs, files in os.walk(parentDir):

    if not not files and any(".txt" in file for file in files):
        paramList = root.split(". ")[-1].split("\\")
        paramSet = int(root.split(". ")[0].split("\\")[-1])
        param = " - ".join(paramList)

        for model in models:
            modelFiles = list(filter(lambda x: model in x, files))
            csvFile = list(filter(lambda x: '.csv' in x, modelFiles))[0]
            txtFile = list(filter(lambda x: '.txt' in x, modelFiles))[0]
        
            if not dirs:
                folder = root
            else:
                folder = root + dirs

            txtFileDir = os.path.join(folder, txtFile)
            csvFileDir = os.path.join(folder, csvFile)
                
            with open(txtFileDir) as f:
                for line in f:
                    if "Accuracy: " in line:
                        Accuracy = line.split("Accuracy: ")[-1].split("\n")[0]
                    if "Precision: " in line:
                        Precision = line.split("Precision: ")[-1].split("\n")[0]
                    if "Recall: " in line:
                        Recall = line.split("Recall: ")[-1].split("\n")[0]
                    if "Time Trained: " in line:
                        TimeTrained = line.split("Time Trained: ")[-1].split("\n")[0].split("s")[0]
                    if "Incorrect Trade Reduction: " in line:
                        IncorrectTradeReduction = line.split("Incorrect Trade Reduction: ")[-1].split("\n")[0].split('%')[0]
                    if "Correct Trade Reduction: " in line:
                        CorrectTradeReduction = line.split("Correct Trade Reduction: ")[-1].split("\n")[0].split("%")[0]

            historyDF = pd.read_csv(csvFileDir)
            Loss = historyDF['val_loss'].iloc[-1]

            if "Units" in param:
                param = model + "Units" + param.split("Units")[-1]
            insertVals = [model, paramSet, param, Loss, Accuracy, Precision, Recall, \
                IncorrectTradeReduction, CorrectTradeReduction, TimeTrained]
            
            summaryDF.loc[len(summaryDF)] = insertVals

exportFileName = "ParameterTuningSummaryExport.csv"
exportDir = os.path.join(parentDir, exportFileName)

RNNSummaryDF = summaryDF.loc[summaryDF['Model'] == "RNN"].sort_values(by = ['ParamSet']).reset_index(drop = True)
LSTMSummaryDF = summaryDF.loc[summaryDF['Model'] == "LSTM"].sort_values(by = ['ParamSet']).reset_index(drop = True)
GRUSummaryDF = summaryDF.loc[summaryDF['Model'] == "GRU"].sort_values(by = ['ParamSet']).reset_index(drop = True)

summaryDF = RNNSummaryDF.append(LSTMSummaryDF).append(GRUSummaryDF).reset_index(drop = True)

summaryDF.to_csv(exportDir, index = False)
print("Complete")