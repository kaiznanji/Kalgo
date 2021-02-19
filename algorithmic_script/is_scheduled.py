# In this file we will check if each company's grant of stocks is part of a regularly scheduled event
#  (incentive bonus, 10b5-1 plan, performance award, yearly grant etc)

# Import libraries
import bs4 as bs
import requests
import re


# A helper function that checks for key words that identify transaction as being scheduled
def check(transaction_details):
    transaction_details = transaction_details.lower()
    scheduled = ['incentive', 'performance', '10b5-1', 'annual']
    for word in scheduled:
        if word in transaction_details:
            return False
    return True


# A helper function to get the transaction details
def get_recent_message_date(link):
    transaction_details = ''
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    footers = soup.find_all('footnote')
    date = soup.find('periodofreport').text
    for footer in footers:
        transaction_details += ' ' + footer.text
    return transaction_details, date

        
# This function checks if any of the form 4 filings are a part of incentive
#  or performance bonuses or part of a 10b5-1 plan
def scheduled(dictionary):
    tickers = {}
    for key,value in dictionary.items():
        bool_list = []
        for link in value[1]:
            transaction_details = get_recent_message_date(link)[0]
            date = get_recent_message_date(link)[1]
            bool_value = check(transaction_details)            
            bool_list.append(bool_value)
        if (not (False in bool_list)):
            transaction_details = re.sub('[^A-Za-z]+', ' ', transaction_details)
            tickers[key.upper()] = [value[0], transaction_details, date]
        
    return tickers
