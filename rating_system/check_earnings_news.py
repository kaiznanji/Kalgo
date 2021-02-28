# In this file we will check a companies upcoming earnings and recent news headlines through Seeking Alpha

# Import libraries
import requests
import datetime as dt
import time
from time import strptime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re


# Main function
def seekingalpha(tickers):

    # Set options for Firefox Webdriver to avoid detection
    options = Options()
    options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"
    options.headless = True
    options.add_argument("window-size=1280,800")
    options.add_argument("--enable-javascript")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")    
    options.add_argument('--disable-blink-features=AutomationControlled')

    tickers = past_earnings(tickers, options)
    tickers = news(tickers, options)

    return tickers


# EARNINGS

# RATINGS:
#   0  -->  Earnings are far from now and EPS estimate is lower than last quarter
#   1  -->  EPS is higher than last quarter or earnings are approaching (This is a good indicator if a company gives grants before earnings which we know from our script before)

def past_earnings(tickers, options):
    for ticker in tickers:
        url = 'https://seekingalpha.com/symbol/{}/earnings'.format(ticker)

        driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)
        driver.get(url)
        
        upcoming_estimates = driver.find_element_by_id('upcoming-estimates')
        past_estimates = driver.find_element_by_id('past-estimates')

        if 'No estimates available' in upcoming_estimates.text:
            continue

        time.sleep(2) # To mimic human browsing and avoid robot detection

        new_rows = upcoming_estimates.find_elements_by_class_name('row')

        time.sleep(1) 

        past_rows = past_estimates.find_elements_by_class_name('row')
        date = new_rows[0].find_elements_by_tag_name('div')[-1].text

        # If earnings date is not confirmed set it to be in far future (more than 3 weeks)
        if 'Not confirmed' in date:
            date = dt.datetime.now() + dt.timedelta(weeks=4)
        else: 
            date = date.split(" ")[0]
            date = dt.datetime.strptime(date, '%m/%d/%Y')
        
        eps_estimate = new_rows[1].find_elements_by_tag_name('div')[-1].text.split('$')[1]

        time.sleep(1)

        past_eps_estimate = past_rows[1].find_elements_by_tag_name('div')[-1].text.split('$')[1]

        if (((dt.datetime.now() + dt.timedelta(weeks=3)) > date) or (float(eps_estimate) >= float(past_eps_estimate))):
            tickers[ticker] += 1
        
        driver.quit()

    return tickers
        

# NEWS

# RATINGS:
#   0  -->  Negative sentiment in recent press releases and no signal for upcoming conferences to discuss potential good news
#   1  -->  Positive sentiment in recent press releases and no signal for upcoming conferences to discuss potential good news 
#   1  -->  Negative sentiment in recent press releases and signals for upcoming conferences to discuss potential good news
#   2  -->  Positive sentiment in recent press releases and signals for upcoming conferences to discuss potential good news


def news(tickers, options):
    main_url  = 'https://seekingalpha.com'
    
    for ticker in tickers:
        run_once = 0
        sentiment_score = 0
        company = get_company(ticker).lower()
        words = ['company', ticker, company, company.split()[0]]
        link = 'https://seekingalpha.com/symbol/{}/press-releases'.format(ticker)
    
        driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)
        driver.get(link)

        time.sleep(2)
        
        # Find the past 7 articles to analyze
        for article in driver.find_elements_by_css_selector("article[data-test-id='post-list-item']")[:7]:

            time.sleep(3) # To mimic human browsing and avoid robot detection

            texts = ''
            date = article.find_element_by_css_selector("span[data-test-id='post-list-date']").text

            time.sleep(1)

            date = get_date(date)

            time.sleep(1)

            link = article.find_element_by_tag_name('a').get_attribute('href')
            driver2 = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)
            driver2.get(link)
            content = driver2.find_element_by_id('pr-body')
            
            for paragraph in content.find_elements_by_tag_name('p'):
                if (len(paragraph.text.split()) < 10):
                    continue
                paragraph = re.sub("[^A-Za-z]+", ' ', paragraph.text).lower()
                paragraph = re.sub(r'\b\w{1,3}\b', '', paragraph)
                count = 0
    
                # Check if there is any signal for upcoming conferences
                if (run_once == 0):
                    three_weeks_ago = dt.datetime.now() - dt.timedelta(weeks=3)
                    if (date >= three_weeks_ago):
                        if ('conference' in paragraph):
                            count += 1
                        for word in words:
                            if (word in paragraph):
                                count += 1
                                break

                if (count == 2):
                    run_once = 1
                    tickers[ticker] += 1 

                texts += paragraph

            driver2.quit()
            sentiment_score += get_sentiment(texts) 
            
        driver.quit()

        # Check if sentiment of past 7 articles is overall positive
        print(ticker + ': ' + str(sentiment_score))
        if (sentiment_score > 0):
            tickers[ticker] += 1 

    return tickers
            

# A helper function that gets the overall sentiment of a piece of text
def get_sentiment(text):
    analyser = SentimentIntensityAnalyzer()
    score = analyser.polarity_scores(text)
    sentiment = score['compound']
    if (sentiment >= 0.05):
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
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']
