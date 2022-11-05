import pandas as pd
import os
import sys

##A bug was spotted with the history exporting the take profit amount as the take profit price for buy trades..
##Seen to just be on the export/cosmetics side and no impact to backtest figures as original code referred to take profit price correctly. 
##This cleans that up for completeness across all backtests

def BacktestHistoryFixup(HistoryDat):

    checkIdxs = HistoryDat.loc[HistoryDat['action'] == 'buy']
    if all(checkIdxs['Take Profit'] == checkIdxs['Take Profit'].iloc[0]) and \
        all(checkIdxs['Take Profit'] < checkIdxs['Stop Loss']) and \
            all(checkIdxs['Take Profit'] < 0.2):
            fixedHistory = HistoryDat.copy()
            fixedHistory.loc[fixedHistory['action'] == 'buy', 'Take Profit'] = fixedHistory.loc[fixedHistory['action'] == 'buy', 'Take Profit'] + fixedHistory.loc[fixedHistory['action'] == 'buy', 'Executed price']
            return fixedHistory
    else:
        raise Exception ("SOMETHING WEIRD!")

parentFolder = os.path.join(os.getcwd(), 'BacktestResults')

for root, dirs, files in os.walk(parentFolder):
    for name in files:
        if name == 'History.csv':
            fileDir = os.path.join(root, name)
            fileDf = pd.read_csv(fileDir)
            cleanedFile = BacktestHistoryFixup(fileDf)
            cleanedFile.to_csv(fileDir, index = False)
            print("Cleaned File: " + root.split("\\")[-1])
