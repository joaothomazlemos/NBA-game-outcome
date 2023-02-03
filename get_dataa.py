from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time

#SEASONS = list(range(2016, 2023))
SEASONS = [2022]


DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings') # data2 is a directory where standings will be located inside
SCORES_DIR = os.path.join(DATA_DIR, 'scores')

def get_html(url, selector, sleep=7, retries=3): # async allow the code after it to imediatelly execute. 
    html=None
    for i in range(1, retries+1):
        time.sleep(sleep * i) # each try is longer by a sleep multiplication factor

        try:
            with sync_playwright() as p: # istance of playwright object
                browser = p.firefox.launch() # await will actually wait for the async load of the website complete to lauch the browser
                #context = browser.new_context()
                page = browser.new_page() # page will be a new tab
                page.goto(url)
                print(page.title()) # tracking our webscraping progress of tries and sucess
                html = page.inner_html(selector) # we gonna get only part of the html page
        except playwrightTimeout:
            print(f'TimeoutError on the url {url}')
            continue # tries again
        else: # if try suceds
            break
    if html != None:
        return html
    else:
        print('Fail')

def scrapy_season(season):
    url  = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    
    
    html = get_html(url=url, selector='#content .filter')
    if html == None:
        print('still nothing on the first attempt to get the whole page content')
    else:
        print('attempt to get the whole page content succeds!')

        

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    href = [l['href'] for l in links] # l is a hyperlink for a month
    stadings_pages = [f"https://www.basketball-reference.com{l}" for l in href]
#ok
    for url in stadings_pages: # navigate for each month page to save the file name first
        save_path = os.path.join(STANDINGS_DIR, url.split('/')[-1]) # saving in directory the name of the schedule month
        if os.path.exists(save_path):
            continue

        #grabbing table of month
        html = get_html(url=url, selector='#all_schedule')
        if html == None:
            print(f'still nothing on the first attempt to get the whole {url} content')
        else:
            print(f'attempt to get the {url} content succeds!')
        with open (save_path, 'w+') as f:
            f.write(html) # content to be saved in the file  with specified name
    


#scrapping every season
for season in SEASONS:
    scrapy_season(season)
    print(f'scraped season {season} with success')

