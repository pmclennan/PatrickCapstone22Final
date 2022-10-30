# PatrickCapstone22Final
Repo for final Capstone work.
Includes the final backtest functionality used as well as auxiliary functions for other strategy research and a few general utility functions.

Backtest Framework Guide

Basic instructions - "BacktestRunFile_XX.py"
Separate files for type of strategy running as different handling for instantiating strategy objects.
1. Install necessary modules such as datetime, pandas, numpy as well as ta for the strategies and applicable DL libraries (keras used here).
2. Data read - comment out either Backtest.readAndPrepData or Backtest.inputDataAndInfo. Further info below as well as context inside the functions.

    a) Backtest.readAndPrepData method: Set up dates, data directory, time column label and delimitter.
  
    b) Backtest.inputDataAndInfo method: Read data and handling formatting + input currency and frequency.
   
4. Import the trading strategy from the module. Details on how this must be set up are below.
5. Input other parameters for the backtest:
   - Required minimum input rows
   - limits (or skew by using stoploss/takeprofit variables)
   - strategy itself
   - pip size (0.0001 should be correct in most cases)
   - guaranteed_sl
   - broker_cost
   - exportFolder
   - Store indicators (true by default and will override if not applicable (DL))
   - runType (in runBacktest)
 5. Run and review output in the export folder once complete.
  
Important notes
1. The Backtest.readAndPrepData functionality is useful as the user can keep the same dataset and simply tweak start dates, and the Backtest will format the rest. The example datasets and preloaded code are a good example of how this works.  
    It also removes the need for excess formatting in the BacktestRunFile files.  
    However, it assumes the filename is at least in the format for the string splitting to work correctly: "(CurrencyPair)\_(Frequency)\_XX.csv"  
    Export data from MT5 symbols will fit this format, as well as bid/ask concatenated files from the DataConcatenator function (but timecols and delimitter will need to be adjusted).  
2. Trading strategy input must be the class itself for indicators and not an instantiated object. The data input is handled in the strategy.run(data) method. 
  Charting indicators and Deep learning methods can require some pre-instantiation when combined with basic indicators, but the main premise is that a strategy should be able to function and produce its signals simply by running strategy.run(data)  
  
Please contact pmcl2472@uni.sydney.edu.au if any issues and I will attempt to answer as soon as I can.
