from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time



DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings') # data is a directory where standings will be located inside
SCORES_DIR = os.path.join(DATA_DIR, 'scores')
#SEASONS = list(range(2016, 2023))
SEASONS = [2022]


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

#new stuff -------------------------------------------------------------------------

#getting box scores of all months of the selected seasons:

def scrape_boxscores(standing_file): # getting the paths of the htmls
     # here we grab a month and go trough all the month box scores
    with open(standing_file,'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    hrefs = [l.get('href') for l in links]
    box_scores = [href for href in hrefs if href and 'boxscore' in href and '.html' in href]
    box_scores = [f'https://www.basketball-reference.com/{href}' for href in box_scores ]
    #now we have all the links of the box , of all box of the months, of all months together ordered chronologically

    for url in box_scores: # navigate for each month page to save the file name first
            save_path = os.path.join(SCORES_DIR, url.split('/')[-1]) # saving in directory the name of the BOX SCORE
            if os.path.exists(save_path):# if already saved, do the next ( go out to start the loop)
                continue

            #grabbing table of that box score
            html = get_html(url=url, selector='#content') #grabing oly wha we want from id selector
            if not html:
                print(f'still nothing on the first attempt to get the whole {url} content')
                continue # if the link is broken or  laging we go on to the next 
            else:
                print(f'attempt to get the {url} content succeds!')
            
            # -*- coding: utf-8 -*-
            # trying to solve unicode error:
            #UnicodeEncodeError: 'charmap' codec can't encode character '\u0101' in position 346838: character maps to <undefined>

            with open (save_path, 'w+', encoding="utf-8") as f:
                f.write(html) # content to be saved in the file  with specified name


standing_file_names = os.listdir(STANDINGS_DIR) # list of our filename of stanfdings
#filtering just elements we want
standing_file_names = [file for file in standing_file_names if '.html' in file]
#creating the paths names and the scraping
for file in standing_file_names:
    file_path = os.path.join(STANDINGS_DIR, file)
    scrape_boxscores(file_path)


