#Standard library imports
import pandas as pd
import pytz 
import os
import datetime
import sys

#Muting CUDA Warnings 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf 
import keras.models

#Import remaining relevant module files
sys.path.append(os.getcwd())
from signalHandler import signalHandler
from WeeklySummary import get_weekly_summary
from TradeSummary import get_trade_summary
from BacktestRunner import BacktestRunner

###Strategies
##RunFiles
from TradingStrategies.DeepLearning.PredictiveDL import PredictiveDL

##Models
model_folder = os.path.join(os.getcwd(), "DLModels", "Predictors")
model_filename = "RNN_10_M5_Predictor 30-10-2022 12-55-53.h5"
model_loc = os.path.join(model_folder, model_filename)
model = keras.models.load_model(model_loc)

##IMPORTANT
#If you are feeding the data as a directory and wishing the backtesting system to format/prep for report based on filename, please use .readAndPrepData().
#An example of setting up the data directory with specified dates is below.
#If feeding data directly (ie passing a dataframe), please use inputDataAndInfo and supply currency/frequency info for the reporting.

##Data Read setup - method 1
tz = pytz.utc
startDate = datetime.datetime(2021, 10, 13, tzinfo = tz) #Start Date - adjust as necessary
endDate = datetime.datetime(2022, 9, 4, tzinfo = tz) #End Date - adjust as necessary
dataFolder = os.path.join(os.getcwd(), 'Datasets', 'OHLC_BidAsk')
dataFilename = "EURUSD.a_M5_14102021_02092022.csv"
dataDir = os.path.join(dataFolder, dataFilename)
timeCols = 'DATETIME' #Required from knowledge of the dataset. Another example (From MT5 export) is ['DATE', 'TIME']
delimitter = None #Required from knowledge of the dataset. Another example could be "\t"

##Data read - method 2
#data = pd.read_csv(yourDataDir)
#Other data formatting code.

##Remaining Static inputs
inputRows = model.input_shape[1]
limits = [15]
strat = PredictiveDL(model)
strategies = [strat]
one_pip = 0.0001
guaranteed_sl = False
broker_cost = 2*one_pip
exportFolder = os.path.join(os.getcwd(), 'BacktestResults') #Where reports are saved.

runType = 2 #Pertains to how the objects are called (different for DL strategies) as well as if indicator dataframes are saved in history. 
    #Review BacktestRunner.runBacktest for further context

#Note here that the loop is set up such that a range of strategies and limits can be tested in one run.
#But it still works on just a single limit level or strategy, ie have the lists as just one element.

for strategy in strategies:
    try:
        print("Running for strategy: ", strategy().Name)        
    except:
        print("Running for strategy: ", strategy.Name)
    for limit in limits:
        stop_loss = -limit * one_pip 
        take_profit = limit * one_pip 
        Backtest = BacktestRunner(startDate, endDate, inputRows, strategy, exportFolder, storeIndicators = 0)
        Backtest.readAndPrepData(dataDir, delimitter, timeCols)
        #Backtest.inputDataAndInfo(data, "EURUSD", "M1") #Alternative data input example if using a 1 minute EURUSD set.
        Backtest.loadBroker(stop_loss, take_profit, guaranteed_sl, broker_cost)
        Backtest.runBacktest(runType)
        Backtest.runReports(str(limit) + "Limit")
        print("Total PnL: {}".format(round(Backtest.broker.total_profit, 6)))

print("Backtests completed")