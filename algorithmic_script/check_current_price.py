# In this file we eliminate cases when the stock is not below the moving average or volume is low

# Importing libraries
import yfinance as yf
import datetime as dt
import re


def is_stock_down(tick_cik):
    # Eliminate any cases of issuers being reporting owners (people buying stock, we want to find companies)
    for key in list(tick_cik):
        if (key == 'NONE'):
            del tick_cik[key]

        # Just in case we scrape a ticker wrong from the SEC we want to clean it 
        key = re.sub("[^A-Z]+", ' ', key).upper()

        # This is for the edge case when there is trouble reading a ticker 
        start = dt.datetime(2021, 2, 11)
        end = dt.datetime(2021, 2, 13)
        if (yf.download(key, start, end).empty):
            del tick_cik[key]

        end = dt.datetime.now()
        start = end - dt.timedelta(days=90)
        df = yf.download(key, start, end)
        df['MA'] = df['Adj Close'].rolling(window=5).mean()
        volume = df['Volume'][-1]
        if (df['MA'][-1] > df['Adj Close'][-1] or volume < 10000):
            del tick_cik[key]

    return tick_cik
