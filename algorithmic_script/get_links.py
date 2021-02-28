# In this file we plan to scrape the SEC database to find companies
#  with at least three insiders acquiring securities

# Importing libraries
import bs4 as bs
import requests
import string
import datetime as dt
import re


# Get the recent form 4 issuer links with at least 3 insider trades in the past day
def get_all_links():
    main_url = 'https://www.sec.gov'
    url = 'https://www.sec.gov/cgi-bin/current?q1=1&q2=0&q3=4'
    filing_links = {}
    count = 1
    resp = requests.get(url)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    main_date = get_date(soup)
    filings = soup.find('pre')
    filings = filings.find_all('a')
    last_form = filings[0]
    last_CIK = filings[1]
    company_links = []
    form_link = get_form_link(main_url + last_form['href'])
    company_links.append(form_link)
       
    # Iterate through every two values to get each companies CIK and form type
    for form, CIK in zip(filings[2:][0::2], filings[2:][1::2]):
        is_in_range = check_actual_file_date(main_url + form['href'], main_date)
        if ((CIK.text == last_CIK.text) and (form.text == '4') and is_in_range):
            count += 1
            form_link = get_form_link(main_url + form['href'])
            company_links.append(form_link)
    
        else:
            if (count >= 3):
                ticker = get_ticker(company_links[0])
                are_they_acquired = acquired(company_links)

                if (are_they_acquired):
                    filing_links[ticker] = [last_CIK.text, company_links]

            count = 1
            company_links = []
            form_link = get_form_link(main_url + form['href'])
            company_links.append(form_link)
        last_form = form
        last_CIK = CIK
    
    print("|***** LINKS CREATED *****|")
    return filing_links
    

# A helper function to check if enough stocks are acquired
def acquired(links):
    acquiredCount = 0
    disposedCount = 0
    for link in links:
        resp = requests.get(link)
        soup = bs.BeautifulSoup(resp.text, 'html.parser')
        code = soup.find_all('transactionacquireddisposedcode')
        for i in code:
            i = i.text
            i = i.translate({ord(c): None for c in string.whitespace})
            if (i == "A"):
                acquiredCount += 1
            elif (i == "D"):
                disposedCount += 1
    
    # Ensure all insiders are acquiring stock 
    if (disposedCount == 0 and acquiredCount > 0):
        return True
    else:
        return False


# A helper function to get the ticker for a company 
def get_ticker(link):
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    ticker = soup.find('issuertradingsymbol')
    ticker = ticker.text
    return ticker


# A helper function to scrape the form 4 page and get txt file link to parse later on
def get_form_link(link):
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', {'class' : 'tableFile'})
    last_row = table.find_all('tr')[-1]
    link = 'https://www.sec.gov/' + last_row.find('a').get('href')
    return link
 
 
# A helper function to check the actual filing date to make sure
#  we can still get in before news comes out (4 days)
def check_actual_file_date(link, main_date):
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    formContent = soup.find('div', {'class' : 'formContent'})
    recent_date = formContent.find_all('div', {'class' : 'formGrouping'})[-1]
    recent_date = recent_date.find('div', {'class' : 'info'}).text
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d') 
    return check_date_range(main_date, recent_date, 4)


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


# A helper function to get the main date of the filings
def get_date(soup):
    header = soup.find('p')
    date = header.text.partition('\n')[0].lower()
    date = date.split("is")[0]
    date = re.sub("[^0-9]", "", date)
    date = re.sub('\s+', "", date)
    date = dt.datetime.strptime(date, "%Y%m%d")
    return date


