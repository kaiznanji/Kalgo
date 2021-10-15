# In this file we will check a companies upcoming earnings and recent news headlines through Yahoo Finance

# Import libraries
import datetime as dt
import yfinance as yf
import time
from time import strptime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from tqdm import tqdm

# Main function
def seekingalpha(tickers, gecko_path, seleniumOptions):
    tickers = past_earnings(tickers, gecko_path, seleniumOptions)
    print("|***** EARNINGS RATED *****|")
    tickers = news(tickers, gecko_path, seleniumOptions)
    print("|***** NEWS RATED *****|")
    return tickers


# EARNINGS

# RATINGS:
#   0  -->  Earnings are far from now
#   1  -->  Earnings are approaching (This is a good indicator if a company gives grants before earnings which we know from our script before)

def past_earnings(tickers, gecko_path, options):
    keys = list(tickers)
    driver = webdriver.Firefox(executable_path=gecko_path, options=options)

    for i in tqdm(range(len(keys))):
        url = 'https://finance.yahoo.com/quote/{}'.format(keys[i])
        driver.get(url)

        earnings_date = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//td[@data-test='EARNINGS_DATE-value']")))
        if ("N/A" in earnings_date.text):
            continue
        else:
            earnings_date = earnings_date.find_element_by_tag_name("span").text

        month_number = dt.datetime.strptime(re.sub("[^A-Za-z]", "", earnings_date), "%b").month
        date = re.sub("[^0-9,]", "", earnings_date)
        earnings_date = dt.datetime.strptime(str(month_number) + "," + date, '%m,%d,%Y')

        if ((dt.datetime.now() + dt.timedelta(weeks=3)) > earnings_date > dt.datetime.now()):
            tickers[keys[i]] += 1
        
    driver.quit()

    return tickers
        

# NEWS

# RATINGS:
#   0  -->  No signal for upcoming conferences to discuss potential good news
#   1  -->  Signal for upcoming conferences to discuss potential good news 

def news(tickers, gecko_path, options):
    main_url  = 'https://seekingalpha.com'
    keys = list(tickers)
    driver = webdriver.Firefox(executable_path=gecko_path, options=options)

    for i in tqdm(range(len(keys))):
        link = 'https://finance.yahoo.com/quote/{}'.format(keys[i])
    
        driver.get(link)
        titles = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//h3[@class='Mb(5px)']")))
        dates = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='C(#959595) Fz(11px) D(ib) Mb(6px)']")))

        # Find the past 5 articles to analyze
        for title, date in zip(titles[:5], dates[:5]): 
            span_tags = date.find_elements_by_tag_name("span")
            if (len(span_tags) != 2):
                date = ""
            else:
                date = span_tags[-1].text

            if ("hour" in date):
                article_date = dt.datetime.now()
            elif ("day" in date):
                number_of_days = re.sub("[^0-9]", "", date)
                if (number_of_days == ""): # Edge case for when article is yesterday
                    article_date = dt.datetime.now() - dt.timedelta(days=1)
                else:
                    article_date = dt.datetime.now() - dt.timedelta(days=int(number_of_days))
            elif ("month" in date):
                number_of_months = re.sub("[^0-9]", "", date)
                if (number_of_months == ""): # Edge case for when article is last month
                    article_date = dt.datetime.now() - dt.timedelta(weeks=4)
                else:
                    article_date = dt.datetime.now() - dt.timedelta(weeks=int(number_of_months)*4)
            else:
                article_date = dt.datetime.now() - - dt.timedelta(weeks=52)

            title = title.text.lower()

            three_weeks_ago = dt.datetime.now() - dt.timedelta(weeks=3)
            if (article_date >= three_weeks_ago and ('conference' in title or 'meeting' in title)):
                tickers[keys[i]] += 1
                break

    driver.quit()
    return tickers
            

# A helper function that gets the overall sentiment of a piece of text
def get_sentiment(text):
    analyser = SentimentIntensityAnalyzer()
    score = analyser.polarity_scores(text)
    sentiment = score['compound']
    if (sentiment >= 0.50):
        return 1  
    elif ((sentiment > -0.50) and (sentiment < 0.50)):
        return 0
    else:
        return -1
    

# A helper function that grabs the article date
def get_date(date):
    if 'Today' in date:
        date = dt.datetime.now()
    elif 'Yesterday' in date:
        date = dt.datetime.now() - dt.timedelta(days=1)
    else:
        date = date.split(", ")[1]
        month = date.split(". ")[0]
        month = str(strptime(month,'%b').tm_mon) + '/'
        day = date.split(". ")[1]
        year = '/' + str(dt.datetime.now().year)
        date = dt.datetime.strptime(month + day + year, '%m/%d/%Y')
    return date


# A helper function that grabs a company name given a ticker
def get_company(symbol):
    try:
        tickerInfo = yf.Ticker(symbol)
        company_name = tickerInfo.info['longName']
        return company_name
    except:
        return ""
    
