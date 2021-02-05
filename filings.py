# In this file we plan to scrape the SEC database to find companies
#  with at least three insiders acquiring securities

# Importing libraries
import bs4 as bs
import requests
import re
from joblib import dump


# Get the recent form 4 issuer links with at least 3 insider trades in the past day
def get_links():
    main_url = 'https://www.sec.gov/'
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK=&type=4+&owner=include&count=100&action=getcurrent'
    filing_links = []
    boolean = True
    # Run loop until date is not yesterday or no more recent filings
    while boolean:
        links = []
        resp = requests.get(url).text
        soup = bs.BeautifulSoup(resp, features='html.parser')

        # Get all links for filings on each page
        for x in soup.find_all("a"):
            link = x.text + main_url + '/' + x.get('href')
            if "cgi-bin/browse-edgar?action=getcompany&CIK=" in link:
                links.append(link)

        # Narrow the search by Issuer
        for element in range(len(links)):
            if ("Issuer" in links[element]): 
                filing_links.append(links[element].split("(Issuer)",1)[1])
          
        # Pagination process
        try:
            form = soup.find_all('input', {'value' : 'Next 100'})[0]      
            url = form.get('onclick').split("'")[1]
            url = main_url + url
        except:
            boolean = False

    # Find issuers with at least three cases of insider trading
    threeInsiders = list(set([link for link in filing_links if filing_links.count(link) >= 3]))
    return threeInsiders


# A helper function to scrape the form 4 page and get txt file link to parse later on
def get_form_link(link):
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', {'class' : 'tableFile'})
    last_row = table.find_all('tr')[-1]
    link = 'https://www.sec.gov/' + last_row.find('a').get('href')
    return link


# A helper function to get the ticker for a company using marketwatch.com
def get_ticker(companyName):
    try:
        link = 'https://www.marketwatch.com/tools/quotes/lookup.asp?siteID=mktw&Lookup=' + companyName + '&Country=all&Type=All'
        resp = requests.get(link)
        soup = bs.BeautifulSoup(resp.text, 'html.parser')
        results = soup.find('div', {'class' : 'results'})
        tr = results.find_all('tr')[1]
        ticker = tr.find('td').text
        return ticker
    except:
        return "noticker"
        

# Eliminate cases of insiders disposing stocks
def main():
    threeInsiders = get_links()
    insiderLinks = []
    acquisitionLinks = {}
    print("|***** RECENT LINKS ACQUIRED *****|")

    # Get insider transaction links
    for link in threeInsiders:
        link = link.split("&owner")[0]
        link = link.replace("company", "issuer")
        link = link.replace("browse-edgar", "own-disp")
        insiderLinks.append(link)

    # Get links where most insiders are only acquiring securities
    for link in insiderLinks:
        acquisitionCount = 0
        dispositionCount = 0
        form4s = []
        resp = requests.get(link)
        soup = bs.BeautifulSoup(resp.text, 'html.parser')
        table = soup.find("table", {"id": "transaction-report"})
        date = table.find_all('tr')[1].find_all('td')[1].text

        # Get company name to find ticker
        companyName = soup.find('b').text
        companyName = re.sub('[^A-Za-z]+', ' ', companyName)
        ticker = get_ticker(companyName)

        # Iterate through rows in table to check if users are acquiring stocks
        for row in table.find_all('tr')[1:]:
            row_contents = row.find_all('td')
            if row_contents[1].text != date:
                break
            if row_contents[0].text == 'A':
                acquisitionCount += 1
            else:
                dispositionCount += 1
            
            link = 'https://www.sec.gov/' + row.find('a').get('href')
            link = get_form_link(link)
            form4s.append(link)
        
        # Ensure we can find the ticker and at least 85% of insiders are 
        #  acquiring stock (Might be some cases where there is accidental disposing)
        if ticker != "noticker":
            if acquisitionCount/(acquisitionCount+dispositionCount) > 0.85:
                acquisitionLinks[ticker] = form4s

    dump(acquisitionLinks, "links")
    print("|***** FILE CREATED *****|")


if __name__ == '__main__':
    main()