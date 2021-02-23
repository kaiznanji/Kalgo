# In this file we will check a companies upcoming earnings and recent news headlines through Seeking Alpha

# Import libraries
import bs4 as bs
import requests
import datetime as dt

# EARNINGS

# RATINGS:
#   0  -->  Earnings are far from now and EPS estimate is lower than last quarter
#   1  -->  Earnings are approaching (This is a good indicator if a company gives grants before earnings)

def past_earnings(tickers):
    ratings = {}
    for ticker in tickers:
        link = 'https://seekingalpha.com/symbol/{}/earnings'.format(ticker)
        resp = requests.get(link)
        soup = bs.BeautifulSoup(resp.text, 'html.parser')
        upcoming_estimates = soup.find('div', {'id': 'upcoming-estimates'})
        past_estimates = soup.find('div', {'id': 'past-estimates'})
        new_rows = upcoming_estimates.find_all('div')
        past_rows = past_estimates.find_all('div')
        date = new_rows[0].find_all('div')[-1].text
        date = date.split(" ")[0].text
        date =  dt.strptime(date, '%m/%d/%Y')
        eps_estimate = new_rows[1].find_all('div')[-1].text[1:]
        past_eps_estimate = past_rows[1].find_all('div')[-1].text[1:]

        if (((dt.datetime.now() + dt.timedelta(weeks=3)) > date) or (int(eps_estimate) >= int(past_eps_estimate))):
            ratings[ticker] += 1

    return ratings
        

# NEWS

# RATINGS:
#   0  -->  Negative sentiment in recent news and no signal for upcoming conferences to discuss potential good news
#   1  -->  Positive sentiment in recent news and no signal for upcoming conferences to discuss potential good news
#   2  -->  Positive sentiment in recent news and signals for upcoming conferences to discuss potential good news

def news(tickers):
    



