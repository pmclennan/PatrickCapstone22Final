from logging import exception
from unittest import case
import pandas as pd
import pytz 
import os
import datetime
import sys
import time
from collections import deque

from signalHandler import signalHandler
from WeeklySummary import get_weekly_summary
from TradeSummary import get_trade_summary

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #Mute cuda warnings
#import tensorflow as tf 
#import keras.models


class BacktestRunner:
    """
    Class for handling all aspects of the backtest.    
    """

    def __init__(self, startDate, endDate, inputRowSize, strategy, exportParentFolder, storeIndicators = 1):        
        """        
        Parameters:
        startDate (datetime): Starting date of backtest. Required for trimming dataset as well as report functionality.
        endDate (datetime): Ending date of backtest. Also required for trimming dataset as well as report functionality.
        inputRowSize (int): Minimum number of rows required to compute a signal based on the chosen strategy.
        strategy (object): Trading Strategy object. See TradingStrategies for information on structure, and .runBacktest() for further context.
        exportParentFolder (str): Parent directory of where to export results files.
        storeIndicators(int): Integer used as Boolean flag on whether to store indicators calculated by strategy in the history results.
        """

        #Data Preparation attributes
        self.startDate = startDate
        self.endDate = endDate
        self.inputRowSize = inputRowSize
        self.data = None
        self.inputs = deque(maxlen=inputRowSize)

        #Report formatting        
        self.currency = None
        self.frequencyStr = None
        self.exportParentFolder = exportParentFolder

        #Backtesting functionality
        self.broker = signalHandler
        self.strategy = strategy
        self.storeIndicators = storeIndicators

    def inputDataAndInfo(self, data, currency, frequency):
        """
        Function used to read data from a dataframe directly, as opposed to handling formatting from a directory.
        Requires input for currency and frequency to format report.
        Assumes input data has been trimmed to specified period, so re-assigns start/end date.

        Parameters:
        data (pd.DataFrame): Required price data for the currency pair. NB requires the time column to be labelled as 'time'.
        currency(str): A string representation of the currency pair being tested.
        frequency (str): A string representation of the frequency/interval of the data.

        """
        #This function is to be used if feeding a dataframe in directly.
        self.data = data        
        self.startDate = self.data['time'].iloc[self.inputRowSize]
        self.endDate = self.data['time'].iloc[-1]       
        self.currency = currency
        self.frequencyStr = frequency
    
    def readAndPrepData(self, dataDir, delimitter, timeCols):
        """
        Function used to read and format data based on an input directory. Useful as automatically formats things within the object.
        Requires user to know the delimitter and label of time columns in the data file.
        This is set up with the focus of handling MT5 symbol export as well as data from the bid/ask concatenation functions.
        
        Parameters:
        dataDir (str): The directory of the input csv file.
        delimitter (str): The delimitter required on data read. Can be set to None if no delimitter.
        timeCols (str or list(str)): Labels of the time columns in the data folder.
        
        """

        #Set up export filename details
        if "/" in dataDir:
            dataFilename = dataDir.split("/")[-1]
        elif "\\" in dataDir:
            dataFilename = dataDir.split("\\")[-1]
        self.currency = dataFilename.split("_")[0]
        self.frequencyStr = dataFilename.split("_")[1]

        #Read data
        if delimitter is not None:
            fullData = pd.read_csv(dataDir, sep = delimitter, parse_dates = [timeCols])
        else:
            fullData = pd.read_csv(dataDir, parse_dates = [timeCols])

        #Rename/standardize columns as well as localizing time
        fullData.rename(columns = {fullData.columns[0]: 'time'}, inplace = True)
        for oldCol in fullData.columns:
            fullData.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '').lower()}, inplace = True) #Used to handle MT5 Symbol Export.    
                
        fullData['time'] = fullData['time'].dt.tz_localize(tz = pytz.utc)

        if 'bid' in fullData and 'ask' in fullData:
            fullData = fullData[['time', 'open', 'high', 'low', 'close', 'bid', 'ask']]    
        else:
            print("Data does not contain both Bid & Ask - execution will be based on Close price instead.")
            fullData = fullData[['time', 'open', 'high', 'low', 'close']]
        
        #Flag any errors with date inputs
        if self.startDate >= fullData['time'].iloc[-1] or self.startDate > self.endDate or self.endDate <= fullData['time'].iloc[0]:
            print("Date Input error - data dates vs input dates noted below:")
            print("Input start date: {} | Input end date: {}".format(self.startDate, self.endDate))
            print("Data start date : {} | Data end date:  {}".format(fullData['time'].iloc[0], fullData['time'].iloc[-1]))
            raise Exception ("Input time does not work with data dates - please review input dates or dataset")
        
        #Trim the data to the required window
        startIdx = fullData.index[fullData['time'] >= self.startDate][0]
        startIdxAdj = max((startIdx - self.inputRowSize + 1), 0)
        endIdx =  min((fullData.index[fullData['time'] <= self.endDate][-1] + 1), fullData.index[-1])
        self.data = fullData[startIdxAdj:endIdx].reset_index(drop = True)

        #Adjust the start/end date accordingly to line up with the actual data used - for result file naming purposes
        self.startDate = self.data['time'].iloc[self.inputRowSize]
        self.endDate = self.data['time'].iloc[-1]        

    def loadBroker(self, stopLoss, takeProfit, guaranteedSl, brokerCost):
        """
        Function used to set up the broker/signal handler object based on passed parameters.
        See signalHandler for further information on the broker/signal handler inputs.

        Parameters:
        stopLoss (float): Stop loss level in absolute value, not pips.
        takeProfit (float): Take profit level in absolute value, not pips.
        guaranteedSl (bool): Whether to implement a guaranteed stoploss/takeprofit, or if stop conditions are based on the next available price.
            Worth reading online regarding this point as this is topical with the use of brokers and impacts spreads/costs. 
        brokerCost (float): Flat cost of broker in absolute value, not pips.        
        """

        self.broker = self.broker(stopLoss, takeProfit, guaranteedSl, brokerCost, self.data, self.currency, self.frequencyStr, \
            self.startDate, self.endDate, self.storeIndicators)
    
    def runBacktest(self, runType = 1):
        '''
        The main looping function for running the backtest. Implements interaction between the data, trading strategy and signal handler methods.

        Parameters:
        runType(int): The type of run based on the strategy used. Differentiates between standard indicators, deep learning (which return no indicator df) 
            and charting indicator strategies that require instantiation in a different style:
        
            1 - standard indicator strategy. Can return indicatorDF.
            2 - Deep Learning - requires model upon instantiation before input into backtest (otherwise timely), and an indicator strategy class as input. 
                Cannot return indicator DF
            3 - Charting - requires preliminary data upon instantiation before input into backtest. Can return indicatorDF. At this stage only set up/useful with ZigZag/ABCD.
        '''

        startTime = time.time()
        index = 0
        signal = 0

        if runType == 2 and self.storeIndicators == 1:
            print("Note: Indicators can't be saved with history for runType 2 (DL) - Overriding this setting.")
            self.storeIndicators = 0
            self.broker.storeIndicators = 0 #Yes I know this should be a setter method

        #Set up Iteration and print commencing statement
        print("Commencing Backtest")
        for _,row in self.data.iterrows():

            # Loading the inputs array till the 
            # minimum number of inputs are reached
            self.inputs.append(row)
            if len(self.inputs) == self.inputRowSize:

                if runType == 1:
                    #Vanilla indicator strategies
                    strategy = self.strategy()
                    signal, indicatorDf = strategy.run(pd.DataFrame(self.inputs))
                    self.broker.storeSignalAndIndicators(signal, indicatorDf, index)          

                elif runType == 2:
                    signal = self.strategy.run(pd.DataFrame(self.inputs))
                    self.broker.storeSignalAndIndicators(signal, None, index)          
                
                elif runType == 3:
                    signal, indicatorDf = self.strategy.run(pd.DataFrame(self.inputs))
                    self.broker.storeSignalAndIndicators(signal, indicatorDf, index)          

                currentPrice = row['close']

                if 'ask' not in self.data or 'bid' not in self.data:
                    bidPrice = currentPrice
                    askPrice = currentPrice

                else:
                    bidPrice = row['bid']
                    askPrice = row['ask']

                if signal == 1:
                    self.broker.buy(bidPrice, askPrice, index)
                elif signal == -1:
                    self.broker.sell(bidPrice, askPrice, index)
                elif signal == 0:
                    self.broker.checkStopConditions(bidPrice, askPrice, index)
                else:
                    raise Exception ("Unknown Signal!")

            index += 1

            #Show progress
            if index % (round(0.01 * len(self.data), 0)) == 0:
                print("----- Backtest Progress: {}% as at date: {} | PnL: {} pips | Total Trades: {} -----".format(\
                    round(100 * (index/len(self.data))), row['time'].strftime("%Y-%m-%d %H:%M"), round(self.broker.total_profit * 10000, 0), self.broker.trades_total), \
                        end = "\r", flush = True)
                        
        endTime = time.time()
        print("\nTimeConsumed: {}".format(datetime.timedelta(seconds = endTime - startTime)))

    def runReports(self, suffix = None):
        """
        Function for running and exporting reports; History, Summary, Trade Summary and Weekly Summary.
        Will create a subdirectory based on the BacktestRunner export folder input and save the 4 files. 
            The subdirectory is named in the following fashion: {Strategy (where available)}_{Time_Date ran}_{Frequency}_{StartDate}_to_{EndDate}_{Suffix (where available)}

        Parameters:
        suffix (str = None): A suffix that can be appended to the export.
        """
        
        #Folder setup       
        childDir = datetime.datetime.now().strftime("%d%m%y-%H%M%S") + ("_{}_{}__{}_to_{}".format(
            self.currency, self.frequencyStr, self.startDate.date(), self.endDate.date()))
        if suffix is not None:
            childDir = childDir + "_" + str(suffix)
        try:
            try:
                childDir = self.strategy().Name + "_" + childDir
            except:
                childDir = self.strategy.Name + "_" + childDir
        except:
            print("Unavailable to obtain strategy name. Perhaps review structure of strategy class.")

        subfolder = os.path.join(self.exportParentFolder, childDir)
        os.mkdir(subfolder)

        #History
        historyData = self.broker.getHistory()
        historyData = historyData.loc[self.inputRowSize-1:, :].reset_index(drop = True)
        historyFilename = "History.csv"
        historyDir = os.path.join(subfolder, historyFilename).replace('\\', '/')

        #Summary
        summaryData = self.broker.getSummary()
        summaryFilename = "Summary.csv"
        summaryDir = os.path.join(subfolder, summaryFilename).replace('\\', '/')

        #Weekly summary
        weeklySummaryData = get_weekly_summary(historyData, self.frequencyStr)
        weeklySummaryFilename = "Weekly_Summary.csv"
        weeklySummaryDir = os.path.join(subfolder, weeklySummaryFilename).replace('\\', '/')

        #Trade summary
        tradeSummaryData = get_trade_summary(historyData)
        tradeSummaryFilename = "Trade_Summary.csv"
        tradeSummaryDir = os.path.join(subfolder, tradeSummaryFilename).replace('\\', '/')

        #Exporting csvs
        historyData.to_csv(historyDir, index = False)
        summaryData.to_csv(summaryDir, index = False)
        weeklySummaryData.to_csv(weeklySummaryDir, index = False)
        tradeSummaryData.to_csv(tradeSummaryDir, index = False)

        print("Exports finalised\n", summaryData)