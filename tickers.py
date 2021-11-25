# In this file we run the main algorithm that returns our tickers

# Import functions
from elimination_system import *
from rating_system import *

# Import libraries
import time
from selenium.webdriver.firefox.options import Options

# Set options for selenium driver
options = Options()
options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"
options.headless = True
options.add_argument("window-size=1280,800")
options.add_argument("--enable-javascript")   
options.add_argument("start-maximized")
options.add_argument('--disable-blink-features=AutomationControlled')

# Path for gecko driver
gecko_path = '/usr/local/bin/geckodriver'

# For testing only
def print_ticker_cik(tickers_cik):
    return [key + " " + value[0] for key, value in tickers_cik.items()]


# Elimination System for Tickers
def elimination_system():
    links = get_all_links(gecko_path, options)
    print("|***** LINKS CREATED *****|", print_ticker_cik(links))
    tickers_cik = is_stock_down(links)
    print("|***** STOCK DOWN ELIMINATED *****|", print_ticker_cik(tickers_cik))
    tickers_cik = scheduled(tickers_cik)
    print("|***** SCHEDULED ELIMINATED *****|", print_ticker_cik(tickers_cik))
    return tickers_cik


# Rating System for Tickers
def rating_system(tickers_cik):
    # Create a list of ciks and initialize rating system
    values = []
    tickers = {}
    keys = list(tickers_cik)
    for key, value in tickers_cik.items():
        values.append(value)
        tickers[key] = 0

    ratings = shady_past(tickers, values, gecko_path, options)
    print("|***** SHADY PAST RATED *****|")
    ratings = seekingalpha(ratings, gecko_path, options)

    # Delete tickers that have score of 1 or less
    for key in list(ratings):
        if (ratings[key] <= 1):
            del ratings[key]

    return ratings
    

def main():
    start = time.time()
    tickers_cik = elimination_system()
    ratings = rating_system(tickers_cik)
    print("The process took:", round((time.time()-start)/60, 2), "minutes")
    print("Ticker ratings are:", ratings)

if __name__ == '__main__':
    main()

    
# After main signal is done learn more on machine learning algorithms to orchestrate buy and sell orders given a ticker

