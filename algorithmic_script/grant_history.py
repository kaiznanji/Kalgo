# In this file we input the tickers given with potential shady
#  activity and look at grant history to check if the stock is worth investing in


# Import libraries
import bs4 as bs
import requests
import yfinance as yf
import datetime as dt
import re

# Import functions from other files
from algorithmic_script.get_links import get_form_link
from algorithmic_script.is_scheduled import get_recent_message_date


def shady_past(tick_cik):
    main_url = 'https://www.sec.gov'
    main_date = get_date()
    last_year = main_date - dt.timedelta(days=365)
    
    for key, value in tick_cik.copy().items():
        run_once = 0
        i = 0
        j = 0
        count = 1
        boolean = True
        cik = value[0]
        main_message = value[1]
        first_date = value[2]
        url = 'https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK={}'.format(cik)
        while boolean:
            resp = requests.get(url)
            soup = bs.BeautifulSoup(resp.text, 'html.parser')
            table = soup.find("table", {"id": "transaction-report"})
            tr_tags = table.find_all('tr')[1:]       
            row_contents = tr_tags[0].find_all('td')
            date = row_contents[1].text
            date = dt.datetime.strptime(date, '%Y-%m-%d') 

            # Iterate through rows in table to look for last years grant
            while not check_date_range(last_year, date, 30):
                if (i == (len(tr_tags) - 1)):
                    # Pagination process
                    try:
                        form = soup.find_all('input', {'value' : 'Next 80'})[0]      
                        url = form.get('onclick').split("'")[1]
                        url = main_url + url
                        i = 0
                        
                    except:
                        boolean = False

                    break
                
                i += 1
                row_contents = tr_tags[i].find_all('td')
                date = row_contents[1].text
                if (date == first_date):
                    count += 1

                date = dt.datetime.strptime(date, '%Y-%m-%d')  

            if (run_once == 0):
                count_down = count
                run_once += 1

            while (check_date_range(last_year, date, 30)):
                is_last_years_grant = False
                link = main_url + row_contents[4].find('a')['href']
                form_link = get_form_link(link)              
                recent_message = get_recent_message_date(form_link)[0]
                if main_message != '':
                    is_last_years_grant = compare_details(main_message, recent_message)

                if (row_contents[0].text == 'A' and count_down == 0):
                    is_last_years_grant = True
                elif (row_contents[0].text == 'D'):
                    count_down = count
                else:
                    count_down -= 1 
                
                if (is_last_years_grant):
                    recorded_date = check_filing_date(link)
                    if (check_date_range(last_year, recorded_date, 7)):
                        recorded_closing = yf.download(key, recorded_date, recorded_date + dt.timedelta(days=1))['Adj Close'].values[0]
                        two_week_date = recorded_date + dt.timedelta(days=14)
                        two_week_closing = yf.download(key, two_week_date, two_week_date + dt.timedelta(days=1))['Adj Close'].values[0]
                        roi = ((two_week_closing - recorded_closing)/recorded_closing) * 100
                        
                        if (roi < 5):
                            del tick_cik[key]

                    elif (date < last_year):
                        del tick_cik[key]
                        
                    break
                
                else:
                    if (i == (len(tr_tags) - 1)):
                        # Pagination process
                        try:
                            form = soup.find_all('input', {'value' : 'Next 80'})[0]      
                            url = form.get('onclick').split("'")[1]
                            url = main_url + url
                            i = 0
                        
                        except:
                            boolean = False

                        break
                    i += 1
                    row_contents = tr_tags[i].find_all('td')
                    date = row_contents[1].text
                    date = dt.datetime.strptime(date, '%Y-%m-%d') 

            if (i != (len(tr_tags) - 1) and i != 0):
                break
    
    # Return final dictionary of remaining tickers
    if tick_cik:
        for key, value in tick_cik.items():
            tick_cik[key] = value[0]
    
    return tick_cik


# A helper function to get the main date of the filings
def get_date():
    url = 'https://www.sec.gov/cgi-bin/current?q1=1&q2=0&q3=4'
    resp = requests.get(url)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    header = soup.find('p')
    date = header.text.partition('\n')[0].lower()
    date = date.split("is")[0]
    date = re.sub("[^0-9]", "", date)
    date = re.sub('\s+', "", date)
    date = dt.datetime.strptime(date, "%Y%m%d")
    return date


# A helper function to compare the messages to find the annual filings last year
def compare_details(main_message, recent_message):
    recent_message = re.sub('[^A-Za-z]+', ' ', recent_message).lower()  
    main_message = main_message.lower().split()
    totalWords = len(main_message)
    wordsInRecentMessage = 0
    for word in main_message:
        if word in recent_message:     
            wordsInRecentMessage += 1
        
    if (wordsInRecentMessage / totalWords) >= 0.90:
        return True
    else:
        return False



# A helper function to check if a date is in a certain range of another date
def check_date_range(main_date, date, range):
    added_days = dt.timedelta(days=range)
    if date > main_date:
        date -= added_days
        if date <= main_date:
            return True
        else:
            return False
    else:
        date += added_days
        if (date >= main_date):
            return True
        else:
            return False


# A helper function to check the filing date
def check_filing_date(link):
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    formContent = soup.find('div', {'class' : 'formContent'})
    recent_date = formContent.find_all('div', {'class' : 'formGrouping'})[0]
    recent_date = recent_date.find('div', {'class' : 'info'}).text
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d') 
    return recent_date

