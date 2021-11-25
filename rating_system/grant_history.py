# In this file we input the tickers given with potential shady
#  activity and look at grant history to check if the stock is worth investing in
# We also look at past grants and see if typically a company's stock goes up after
#  grants. This corresponds to a rating system that can be seen below.


# Import libraries
import bs4 as bs
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import yfinance as yf
import datetime as dt
import re
from tqdm import tqdm

# Import functions from other files
from elimination_system.get_links import get_form_link
from elimination_system.is_scheduled import get_recent_message

# RATINGS:
#   0  -->  There are zero to one cases when a company gives grants their stock price shoots up
#   1  -->  Sometimes when a company gives grants their stock price shoots up
#   2  -->  Majority of the time when a company gives grants their stock price shoots up or if they moved grants to earlier in the year


def shady_past(tickers, values, gecko_path, options):
    main_url = 'https://www.sec.gov'
    keys = list(tickers)
    driver = webdriver.Firefox(executable_path=gecko_path, options=options)
    main_date = get_date(driver)
    last_year = main_date - dt.timedelta(weeks=52)
    last_month = main_date - dt.timedelta(weeks=4)

    for i in tqdm(range(len(values))):
        # Intialize variables to track correlation between stock grants given out and stock price shooting up
        three_counter = 0
        stock_up_counter = 0
        moved_up_grants = False
        page_exists = True
        page_number = 0
        count = 0
        cik = values[i][0]
        main_message = values[i][1]
        url = 'https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK={}'.format(cik)

        while (page_exists and page_number < 3):
            driver.get(url)

            # Obtain data from table
            table = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//table[@id='transaction-report']")))
            rows = table.find_elements_by_tag_name("tr")[1:]
            last_row_contents = rows[0].find_elements_by_tag_name('td')
            row_pos = 0

            # Loop through values to start at a month ago(so we can check if stock went up)
            while (row_pos < len(rows)-1 and last_row_contents[1].text != "-" and last_month < dt.datetime.strptime(last_row_contents[1].text, '%Y-%m-%d')):
                row_pos += 1
                
                # Initializing last row content into variables to allow comparison in loop only on first page so we can track count through page switches
                last_row_contents = rows[row_pos].find_elements_by_tag_name('td')
                last_acqusition_value = last_row_contents[0].text
                last_date = last_row_contents[1].text
                last_form_link = last_row_contents[4].find_element_by_tag_name('a').get_attribute('href')
                last_form = last_row_contents[4].text

            # Loop through rows to find dates where 3+ individuals recieved grants
            while (row_pos != len(rows)):
                row_contents = rows[row_pos].find_elements_by_tag_name('td')
                acqusition_value = row_contents[0].text
                date = row_contents[1].text
                form_link = row_contents[4].find_element_by_tag_name('a').get_attribute('href')
                form = row_contents[4].text

                # Exception case when date is not provided
                if (date == "-"):
                    row_pos += 1
                    continue

                if ((form == '4') and acqusition_value == 'A' and (date == last_date)):
                    count += 1

                else:
                    if (count >= 3):
                        three_counter += 1
                        # Check if stock went up by more than 5 percent in four weeks and add to stock_up_counter if it did
                        filing_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
                        four_week_date = filing_date + dt.timedelta(weeks=4)
                        try:
                            closing_values = yf.download(keys[i], filing_date, four_week_date + dt.timedelta(days=1), progress=False)['Adj Close'].values
                            filing_closing = closing_values[0]
                            four_week_closing = closing_values[-1]
                            roi = ((four_week_closing - filing_closing)/filing_closing) * 100
                            if (roi >= 5):
                                stock_up_counter += 1
                        except Exception as e:
                            print("Error in retrieving closing prices")

                    count = 1
                
                # Check if they moved grants to earlier in the year
                dt_last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
                if (last_acqusition_value == "A" and last_form == "4" and check_date_range(last_year, dt_last_date, 30)):
                    text_file_link = get_form_link(last_form_link, cik)
                    recent_message = get_recent_message(text_file_link)
                    if main_message != '':
                        is_last_years_grant = compare_details(main_message, recent_message)
                        if (is_last_years_grant and (dt_last_date >= last_year + dt.timedelta(weeks=1))):
                            moved_up_grants = True

                last_date = date
                last_form = form
                last_form_link = form_link
                last_acqusition_value = acqusition_value
                row_pos += 1

            # Pagination process when you reach last element
            try:
                form = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//input[@value='Next 80']")))
                url = form.get_attribute('onclick').split("'")[1]
                url = main_url + url
                page_number += 1
            except:
                page_exists = False

        if (not moved_up_grants):
            if (three_counter >= 3):  
                percentage = stock_up_counter / three_counter
                if (percentage >= 0.90): 
                    tickers[keys[i]] += 2
                elif (0.90 > percentage >= 0.50):
                    tickers[keys[i]] += 1
        else:
            tickers[keys[i]] += 2

    driver.quit()
    return tickers


# A helper function to get the main date of the filings
def get_date(driver):
    url = 'https://www.sec.gov/cgi-bin/current?q1=1&q2=0&q3=4'
    driver.get(url)
    header = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "p")))
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
def check_filing_date(link, gecko_path, options):
    driver = webdriver.Firefox(executable_path=gecko_path, options=options)
    driver.get(link)
    formContent = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='formContent']")))
    recent_date = formContent.find_element_by_xpath("//div[@class='formGrouping']")
    recent_date = recent_date.find_element_by_xpath("//div[@class='info']").text
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    driver.quit()
    return recent_date
