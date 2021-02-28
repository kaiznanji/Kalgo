# In this file we will provide a rating to each stock based on past grant history

# Import libraries
import bs4 as bs
import requests


# RATINGS:
#   0  -->  There are zero to one cases when a company gives grants their stock price shoots up
#   1  -->  Sometimes when a company gives grants their stock price shoots up
#   2  -->  Majority of the time when a company gives grants their stock price shoots up


def good_grants(tick_cik):
    ciks = []
    tickers = tick_cik

    # Create a list of ciks and initialize rating system
    for key, value in tick_cik.items():
        ciks.append(value)
        tickers[key] = 0
    
    for cik in ciks:
        url = 'https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK={}'.format(cik)
        resp = requests.get(url)
        soup = bs.BeautifulSoup(resp.text, 'html.parser')
        # start at maybe a month before today to look at
        # go all the way until you hit today - 3 years
        # look for acquisitions and at least 3 acquisitions on the same date
        # then correspond that to the stock value 2-3 weeks from now and check roi
        # add each profit to a counter and check at the end how many had profits relative to total