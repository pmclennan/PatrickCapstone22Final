#Standard library imports
import pandas as pd
import pytz 
import os
import datetime
import sys

#Import remaining relevant module files
sys.path.append(os.getcwd())
from signalHandler import signalHandler
from WeeklySummary import get_weekly_summary
from TradeSummary import get_trade_summary
from BacktestRunner import BacktestRunner

###Trading Strategies Import
##Basic
from TradingStrategies.Basic.Bollinger_Bands import Bollinger_Bands
from TradingStrategies.Basic.MACD_Crossover import MACD_Crossover
from TradingStrategies.Basic.Commodity_Channel_Index import Commodity_Channel_Index
from TradingStrategies.Basic.Parabolic_SAR import Parabolic_SAR
from TradingStrategies.Basic.Stochastic_Oscilator import Stochastic_Oscilator

##Combination
from TradingStrategies.Combination.DonchianChannel_CCI_SMA import DC_CCI_SMA
from TradingStrategies.Combination.pSAR_SO import pSAR_SO
from TradingStrategies.Combination.three_rsp import ThreeRSP
from TradingStrategies.Combination.MACD_Stochastic_Crossover import MACDStochasticCrossover
from TradingStrategies.Combination.DonchianChannel_CCI import DC_CCI
from TradingStrategies.Combination.MovingAverage_BollingerBands import MA_BB
from TradingStrategies.Combination.CCI_pSAR_DC_BB import CCI_pSAR_DC_BB

##Patterns
#TODO

##IMPORTANT
#If you are feeding the data as a directory and wishing the backtesting system to format/prep for report based on filename, please use .readAndPrepData().
#An example of setting up the data directory with specified dates is below.
#If feeding data directly (ie passing a dataframe), please use inputDataAndInfo and supply currency/frequency info for the reporting.

##Data Read setup - method 1
tz = pytz.utc
startDate = datetime.datetime(2017, 9, 3, tzinfo = tz) #Start Date - adjust as necessary
endDate = datetime.datetime(2021, 9, 4, tzinfo = tz) #End Date - adjust as necessary
dataFolder = os.path.join(os.getcwd(), 'Datasets', 'OHLC_Only')
dataFilename = "EURUSD.a_M5_201709040000_202109031210.csv"
dataDir = os.path.join(dataFolder, dataFilename)
timeCols = ['<DATE>', '<TIME>'] #Required from knowledge of the dataset. Another example (From MT5 export) is ['DATE', 'TIME']
delimitter = "\t" #Required from knowledge of the dataset. Another example could be "\t"

 
##Data read - method 2
#data = pd.read_csv(yourDataDir)
#Other data formatting code.

##Remaining Static inputs
inputRows = 50
#limits = [15]
stop_loss = -15
take_profit = 30
strategies = [CCI_pSAR_DC_BB]
one_pip = 0.0001
guaranteed_sl = False
broker_cost = 2*one_pip
exportFolder = os.path.join(os.getcwd(), 'BacktestResults') #Where reports are saved.

runType = 1 #Pertains to how the objects are called (different for DL strategies) as well as if indicator dataframes are saved in history. 
    #Review BacktestRunner.runBacktest for further context

#Note here that the loop is set up such that a range of strategies and limits can be tested in one run.
#But it still works on just a single limit level or strategy, ie have the lists as just one element.

for strategy in strategies:
    try:
        print("Running for strategy: ", strategy().Name)        
    except:
        print("Running for strategy: ", strategy.Name)
    stop_loss = stop_loss * one_pip 
    take_profit = take_profit * one_pip 
    Backtest = BacktestRunner(startDate, endDate, inputRows, strategy, exportFolder)
    Backtest.readAndPrepData(dataDir, delimitter, timeCols)
    #Backtest.inputDataAndInfo(data, "EURUSD", "M1") #Alternative data input example if using a 1 minute EURUSD set.
    Backtest.loadBroker(stop_loss, take_profit, guaranteed_sl, broker_cost)
    Backtest.runBacktest(runType)
    if abs(stop_loss) == abs(take_profit):
        Backtest.runReports(str(int(abs(stop_loss)/one_pip)) + "Limit")
    else:
        Backtest.runReports(str(int(abs(stop_loss)/one_pip)) + "SL" + str(int(take_profit/one_pip)) + "TP")
    print("Total PnL: {}".format(round(Backtest.broker.total_profit, 6)))

print("Backtests completed")