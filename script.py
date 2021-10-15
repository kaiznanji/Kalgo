# In this file we run the main algorithm that returns our tickers

# Import functions
from algorithmic_script import *
from rating_system import *

# Import options from selenium
from selenium.webdriver.firefox.options import Options

import time
# tickers_cik = {'AI': ['1577526', ' Provided the Reporting Person remains a director of the Company and attends in person the regularly scheduled meeting of the Board during each fiscal quarter commencing on October the Vesting Commencement Date then of the shares subject to the option shall vest on the last day of such fiscal quarter the Quarterly Shares during the term of the option provided however if the Reporting Person fails to attend any such regularly scheduled meeting then vesting for the Quarterly Shares shall not occur and will be suspended any such suspended Quarterly Shares being referred to collectively as the Suspended Shares For any Suspended Shares such shares shall vest only following the fifth anniversary of the applicable Vesting Commencement Date if the Reporting Person satisfies the attendance requirements in subsequent periods ', '2021-10-06'], 'HIPO': ['1828105', ' th of the shares underlying the option vest on each quarterly anniversary measured from September for the first four quarters and th of the shares shall vest quarterly thereafter for the remaining four quarters subject to the Reporting Person continuing to provide services to the Issuer through the applicable vesting date ', '2021-09-10'], 'IRM': ['1020569', ' Pursuant to the Reporting Person s election to participate in the Iron Mountain Incorporated Directors Deferred Compensation Plan the Plan the shares of phantom stock the Phantom Shares will become payable in shares of Iron Mountain Incorporated common stock Common Stock on various dates selected by the Reporting Person or as otherwise provided in the Plan Each Phantom Share is the economic equivalent of one share of Common Stock These shares give effect to dividends paid on Common Stock as if reinvested in Phantom Shares ', '2021-10-06'], 'JLL': ['1037976', ' Represents shares elected to be received in lieu of annual cash retainer and annual cash committee retainer payable in advance for the fourth quarter of fiscal year in accordance with prior election under the Non Executive Director Compensation Plan and the U S Deferred Compensation Plan The receipt of these shares has been deferred pursuant to the Non Executive Director Compensation Plan ', '2021-10-06'], 'LYTS': ['763532', ' Common Shares held in the LSI Industries Inc Non Qualified Deferred Compensation Plan ', '2021-10-06'], 'PRA': ['1127703', ' These shares were acquired from ProAssurance Corporation under its Director Deferred Stock Compensation Plan the Plan and are exempt under Rule b The Board of Directors may grant shares to directors at each annual meeting as part of their compensation and directors may elect to defer payment of the shares under the Plan Any deferred shares are then credited to the electing director s account under the Plan and accrue dividends as permitted by the Plan On each subsequent dividend payment date the accrued dividends are credited to the directors deferred stock accounts as additional whole shares of deferred stock at the market price on the dividend payment date Amounts attributable to fractional shares are denominated in dollars and applied toward additional shares of deferred stock on the next dividend payment date ', '2021-10-08'], 'RPM': ['110621', ' Represents a grant of shares of Common Stock issued pursuant to the RPM International Inc Restricted Stock Plan for Directors ', '2021-10-06'], 'SNCE': ['1819113', ' Pursuant to the business combination of LifeSci Acquisition II Corp and Science Inc Old Science as contemplated by that certain agreement and plan of merger dated May the Merger Agreement a each share of common stock of Old Science outstanding immediately prior to the effective time of the business combination was converted into approximately shares of the Issuer s Common Stock b the Conversion Ratio and b each outstanding stock option of Old Science was converted into a corresponding option to purchase shares of the Issuer s Common Stock as adjusted for the Conversion Ratio Stock Option is currently vested and exercisable as to of the underlying shares and the remaining shares will vest in equal monthly installments until fully vested on June ', '2021-10-06']}

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

