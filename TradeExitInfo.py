import os
import sys
import pandas as pd
import sys
import numpy as np
sys.path.append(os.getcwd())

def TradeExitInfo(historyDat):

    tradeHist = historyDat.loc[historyDat['action'] != 'hold'].reset_index(drop = True)
    tradeHist = tradeHist[['time', 'bid', 'ask', 'signal', 'action', 'position', 'Executed price', 'Take Profit', 'Stop Loss', 'P/L']]
    tradeHist['ExitInfo'] = [""] * len(tradeHist)

    for i in range(1, len(tradeHist), 2):

        if tradeHist['action'].iloc[i] == 'close long' and tradeHist['action'].iloc[i-1] == 'buy':
            TP = tradeHist['Take Profit'].iloc[i-1]
            SL = tradeHist['Stop Loss'].iloc[i-1]
            BP = tradeHist['bid'].iloc[i]
            if (SL <= BP <= TP) and tradeHist['signal'].iloc[i] == -1:
                tradeHist['ExitInfo'].iloc[i] = 'CloseSignal'
            elif SL >= BP:
                tradeHist['ExitInfo'].iloc[i] = 'StoppedOut'
            elif TP <= BP:
                tradeHist['ExitInfo'].iloc[i] = 'TookProfit'
            else:
                print("UNKNOWN REASON!")

        elif tradeHist['action'].iloc[i] == 'close short' and tradeHist['action'].iloc[i-1] == 'short':
            TP = tradeHist['Take Profit'].iloc[i-1]
            SL = tradeHist['Stop Loss'].iloc[i-1]
            AP = tradeHist['ask'].iloc[i]
            if (SL >= AP >= TP) and tradeHist['signal'].iloc[i] == 1:
                tradeHist['ExitInfo'].iloc[i] = 'CloseSignal'
            elif SL <= AP:
                tradeHist['ExitInfo'].iloc[i] = 'StoppedOut'
            elif TP >= AP:
                tradeHist['ExitInfo'].iloc[i] = 'TookProfit'
            else:
                print("UNKNOWN REASON!")

        else:
            print("UNKNOWN SITUATION!")

    closeSignalTotal = sum(tradeHist.loc[tradeHist['ExitInfo'] == 'CloseSignal', 'P/L']) * 10000
    closeSignalAvg = round(np.mean(tradeHist.loc[tradeHist['ExitInfo'] == 'CloseSignal', 'P/L']) * 10000, 2)
    closeSignalN = len(tradeHist.loc[tradeHist['ExitInfo'] == 'CloseSignal'])

    TPTotal = sum(tradeHist.loc[tradeHist['ExitInfo'] == 'TookProfit', 'P/L']) * 10000
    TPAvg = round(np.mean(tradeHist.loc[tradeHist['ExitInfo'] == 'TookProfit', 'P/L']) * 10000, 2)
    TPN = len(tradeHist.loc[tradeHist['ExitInfo'] == 'TookProfit'])

    SLTotal = sum(tradeHist.loc[tradeHist['ExitInfo'] == 'StoppedOut', 'P/L']) * 10000
    SLAvg = round(np.mean(tradeHist.loc[tradeHist['ExitInfo'] == 'StoppedOut', 'P/L']) * 10000, 2)
    SLN = len(tradeHist.loc[tradeHist['ExitInfo'] == 'StoppedOut'])

    totalPnL = round(tradeHist['P/L'].sum() * 10000, 2)
    avgPnL = round(tradeHist.loc[tradeHist['P/L'] != 0, 'P/L'].mean() * 10000, 2)
    NTrades = len(tradeHist.loc[tradeHist['P/L'] != 0, 'P/L'])    

    totalVals = [closeSignalTotal, TPTotal, SLTotal, totalPnL]
    avgVals = [closeSignalAvg, TPAvg, SLAvg, avgPnL]    
    NVals = [closeSignalN, TPN, SLN, NTrades]

    summaryDF = pd.DataFrame(data = {'TotalPnL': totalVals, 'AveragePnL': avgVals, 'Number': NVals}, index = ['CloseSignal', 'TookProfit', 'StoppedOut', 'Aggregate'])

    return summaryDF

parentFolder = os.path.join(os.getcwd(), "BacktestResults", "BasicIndicators", "M5_2021-2022")
backtestFolder = os.path.join(parentFolder, "CCI_291022-150650_EURUSD.a_M5__2021-10-14_to_2022-09-02_15Limit")
historyDir = os.path.join(backtestFolder, "History.csv")

historyDat = pd.read_csv(historyDir)

tradeExitInfoDF = TradeExitInfo(historyDat)

exportFilename = "TradeExitBreakdown.csv"
exportDir = os.path.join(backtestFolder, exportFilename)

tradeExitInfoDF.to_csv(exportDir)

print("Complete")