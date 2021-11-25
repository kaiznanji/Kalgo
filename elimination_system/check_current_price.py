# In this file we eliminate cases when the stock is not below the moving average or volume is low

# Importing libraries
import yfinance as yf
import datetime as dt
import re


def is_stock_down(tick_cik):
    # Eliminate any cases of issuers being reporting owners (people buying stock, we want to find companies)
    i = 0
    for key in list(tick_cik):
        if (key == 'NONE' or key == 'N/A'):
            del tick_cik[key]
            continue

        # Just in case we scrape a ticker wrong from the SEC we want to clean it 
        temp_key = re.sub("[^A-Z]+", ' ', key).upper()

        # Testing if stock data for the given ticker exists
        try:
            start = dt.datetime(2021, 2, 11)
            end = dt.datetime(2021, 2, 13)
            df = yf.download(temp_key, start, end)
            row = df.iloc[0].values
        except:
            del tick_cik[key]
            continue

        if (df.empty or len(row) > 7):
            del tick_cik[key]
            continue

        end = dt.datetime.now()
        start = end - dt.timedelta(days=90)
        df = yf.download(temp_key, start, end, progress=False)
        
        df['MA'] = df['Adj Close'].rolling(60).mean()
        
        volume = df['Volume'][-1]
        
        if (df['MA'][-1] < df['Adj Close'][-1] or volume < 25000):
            del tick_cik[key]

        # Replace key with cleaned key
        if (temp_key != key):
            tick_cik[temp_key] = tick_cik[key]
            del tick_cik[key]

    return tick_cik
