# In this file we run the main algorithm that returns our tickers

# Import functions
from algorithmic_script.get_links import get_all_links
from algorithmic_script.is_scheduled import scheduled
from algorithmic_script.grant_history import shady_past
from algorithmic_script.check_current_price import is_stock_down
from rating_system.check_earnings import 
from rating_system.rate_grants import 


def main():
    links = get_all_links()
    tickers_cik = is_stock_down(links)
    tickers_cik = scheduled(tickers_cik)
    tickers_cik = shady_past(tickers_cik)

    # CHANGE FROM ELIMINATION TO RATING SYSTEM
    # check earnings
    # look at past consecutive grants of 3 or more and see if stock went up or down and create a rating corresponding to that
    # maybe create another algorithm that looks at bloomberg api for news 
    return tickers_cik

if __name__ == '__main__':
    main()
    
    
