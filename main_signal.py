# In this file we run the main algorithm that returns our tickers

# Import functions
from algorithmic_script.get_links import get_all_links
from algorithmic_script.is_scheduled import scheduled
from algorithmic_script.grant_history import shady_past
from algorithmic_script.check_current_price import is_stock_down
from rating_system.check_earnings import past_earnings
from rating_system.rate_grants import news


def main():
    
    # Elimination System for Tickers
    links = get_all_links()
    tickers_cik = is_stock_down(links)
    tickers_cik = scheduled(tickers_cik)
    tickers_cik = shady_past(tickers_cik)

    # Rating System for Tickers
    tickers = good_grants(tickers_cik)
    tickers = past_earnings(tickers)
    tickers = news(tickers)
    
    return tickers_cik

if __name__ == '__main__':
    main()
    
    
# After main signal is done learn more on machine learning algorithms to orchestrate buy and sell orders given a ticker

