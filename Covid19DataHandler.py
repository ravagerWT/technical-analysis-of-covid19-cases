import pandas as pd
from typing import Type

from MACD_Plot import calculate_macd
from RSI_Plot import calculate_rsi

def getCovidDataFrame(DATA_FILE_PATH: str, country: str = 'Taiwan*'):
    df = pd.read_csv(DATA_FILE_PATH, sep=',')
    df.drop(labels=['Province/State', 'Lat', 'Long'], axis=1, inplace=True)

    # extract Taiwan dataset from DataFrame
    filter = df['Country/Region'] == country
    df_tw = df[filter]

    # transpose DataFrame
    df_tw_transpose = df_tw.transpose()
    df_tw_transpose.reset_index(inplace=True)
    
    # delete first rows
    df_tw_transpose.drop([0],inplace=True)

    # modify index names
    df_tw_transpose.columns=['date', 'accu_cases']

    # calculate daily cases. ref:https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/05_add_columns.html
    df_tw_transpose['daily_cases'] = df_tw_transpose['accu_cases'] - df_tw_transpose['accu_cases'].shift(1)
    
    # remove the NaN in daily_cases. ref: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.iat.html
    df_tw_transpose.iat[0, 2] = 0
    
    # replacing negative value in daily_cases. ref: https://stackoverflow.com/questions/49681363/replace-negative-values-in-single-dataframe-column
    df_tw_transpose.daily_cases = df_tw_transpose.daily_cases.mask(df_tw_transpose.daily_cases.lt(0),0)

    # insert MACD data to dataframe
    MACD_line, MACD_Signal_line, MACD_Histogram = calculate_macd(df_tw_transpose, 'daily_cases', 26, 12, 9)
    df_tw_transpose['MACD'] = MACD_line
    df_tw_transpose['MACDs'] = MACD_Signal_line
    df_tw_transpose['MACDh'] = MACD_Histogram

    # insert RSI data to data frame
    rsi_series_6, _ = calculate_rsi(df_tw_transpose, rsi_length=6)
    rsi_series_12, _ = calculate_rsi(df_tw_transpose, rsi_length=12)
    df_tw_transpose['RSI_6'] = rsi_series_6
    df_tw_transpose['RSI_12'] = rsi_series_12

    # replace NaN with 50.  ref: https://stackoverflow.com/questions/26837998/pandas-replace-nan-with-blank-empty-string
    df_tw_transpose.RSI_6.fillna(50,inplace=True)
    df_tw_transpose.RSI_12.fillna(50,inplace=True)

    # transfer date format.  ref:https://www.delftstack.com/zh-tw/howto/python-pandas/how-to-convert-dataframe-column-to-datetime-in-pandas/
    df_tw_transpose['date'] = pd.to_datetime(df_tw_transpose['date'], format="%m/%d/%y")

    return df_tw_transpose

# test function
if __name__ == '__main__':    
    DATA_FILE_PATH = 'time_series_covid19_confirmed_global.csv'
    # DATA_FILE_PATH = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    df = getCovidDataFrame(DATA_FILE_PATH)
    # df.to_csv('tw_case.csv', index=False)
    # print(df)
