# In this file we run the main algorithm that returns our tickers

# Import functions
from get_links import get_all_links
from is_scheduled import scheduled
from grant_history import shady_past
from check_current_price import is_stock_down
from check_earnings import seekingalpha
from rate_grants import good_grants


def main():
    # Elimination System for Tickers
    links = get_all_links()
    tickers_cik = is_stock_down(links)
    tickers_cik = scheduled(tickers_cik)
    tickers_cik = shady_past(tickers_cik)

    # Rating System for Tickers
    tickers = good_grants(tickers_cik)
    tickers = seekingalpha(tickers)

    return tickers_cik

if __name__ == '__main__':
    main()
    
    
# After main signal is done learn more on machine learning algorithms to orchestrate buy and sell orders given a ticker

