# In this file we plan to scrape the SEC database to find companies
#  with at least three insiders acquiring securities

# Importing libraries
import bs4 as bs
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import string
import datetime as dt
import re
import time
from tqdm import tqdm


# Get the recent form 4 issuer links with at least 3 insider trades in the past day
def get_all_links(gecko_path, options):
    # Initializing variables
    url = 'https://www.sec.gov/cgi-bin/current?q1=1&q2=0&q3=4'
    filing_links = {}
    company_links = []
    count = 1

    driver = webdriver.Firefox(executable_path=gecko_path, options=options)
    driver.get(url)
    main_date = get_date(driver)
    filings = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "pre")))
    filings = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    forms = filings[2:][0::2]
    ciks = filings[2:][1::2]

    # Delete "Perform another current events analysis?" in forms array
    del forms[-1]

    last_CIK = filings[1].text
    form_link = get_form_link(filings[0].get_attribute('href'), last_CIK)
    company_links.append(form_link)
    array_size = range(len(forms))

    # Iterate through every two values to get each companies CIK and form type
    for i in tqdm(array_size):
        form = forms[i]
        formHref = form.get_attribute('href')
        CIK = ciks[i].text

        # This line causes the program to take a while longer to run so it is commented out for now until optimized
        #is_in_range = check_actual_file_date(formHref, main_date, gecko_path, options)

        if ((CIK == last_CIK) and (form.text == '4')):
            count += 1
            form_link = get_form_link(formHref, CIK)
            company_links.append(form_link)
    
        else:
            if (count >= 3):
                are_they_acquired = acquired(company_links)

                if (are_they_acquired):
                    ticker = get_ticker(company_links[0])
                    filing_links[ticker] = [last_CIK, company_links]

            count = 1
            company_links = []
            form_link = get_form_link(formHref, CIK)
            company_links.append(form_link)
        last_CIK = CIK

    # To account for last set of companies
    if (count >= 3):
            ticker = get_ticker(company_links[0])
            are_they_acquired = acquired(company_links)

            if (are_they_acquired):
                filing_links[ticker] = [CIK, company_links]
    driver.quit()
    return filing_links
    

# A helper function to check if enough stocks are acquired
def acquired(links):
    acquiredCount = 0
    disposedCount = 0
    for link in links:
        resp = requests.get(link, headers={'User-Agent': 'Spaced Out kaiznanji@spacedout.com', 'Accept-Encoding': 'gzip', 'Host': 'www.sec.gov'})
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
    resp = requests.get(link, headers={'User-Agent': 'Spaced Out kaiznanji@spacedout.com', 'Accept-Encoding': 'gzip', 'Host': 'www.sec.gov'})
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    ticker = soup.find("issuertradingsymbol")
    if (ticker is None):
        return "INVALID"
    else:
        ticker = ticker.text
        return ticker


# A helper function to scrape the form 4 page and get txt file link to parse later on
def get_form_link(link, cik):
    number = link.split("-index")[0].rsplit('/', 1)[1]
    number_without_dashes = re.sub("[^0-9]", "", number)
    txt_link = "https://www.sec.gov/Archives/edgar/data/" + cik + "/" + number_without_dashes + "/" + number + ".txt"
    return txt_link
    
 
# A helper function to check the actual filing date to make sure
#  we can still get in before news comes out (4 days)
def check_actual_file_date(link, main_date, gecko_path, options):
    driver = webdriver.Firefox(executable_path=gecko_path, options=options)
    driver.get(link)
    formContent = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='formContent']")))
    recent_date = formContent.find_elements_by_xpath("//div[@class='formGrouping']")[-1]
    recent_date = recent_date.find_element_by_xpath("//div[@class='info']").text
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d') 
    driver.quit()
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
def get_date(driver):
    header = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "p")))
    date = header.text.partition('\n')[0].lower()
    date = date.split("is")[0]
    date = re.sub("[^0-9]", "", date)
    date = re.sub('\s+', "", date)
    date = dt.datetime.strptime(date, "%Y%m%d")
    return date


