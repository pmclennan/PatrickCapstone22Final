import pandas as pd
import pytz

def MT5SymbolsDataReader(dataDir, utc = True):
    """
    A function to read data from the directory of a file exported from MT5 "View Symbols".
    Handles delimitters, columns and timezones in one function.

    Parameters:
    dataDir (string): The directory of the file location.
    utc (boolean = True): A boolean flag for whether the time column is localized as UTC.

    Returns:
    data (pd.DataFrame): A dataframe of the adjusted data.
    """

    data = pd.read_csv(dataDir, sep = '\t', parse_dates = [['<DATE>', '<TIME>']])

    for oldCol in data.columns:
        data.rename(columns = {oldCol: oldCol.replace('<', '').replace('>', '').replace('_', '').lower()}, inplace = True)
        
    data.rename(columns = {data.columns[0]: 'time'}, inplace = True)
    data = data[['time', 'open', 'high', 'low', 'close']]
    
    if utc:
        data['time'] = data['time'].dt.tz_localize(tz = pytz.utc)

    return data