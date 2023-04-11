from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time
import datetime
import re

#This function will get the html month content of a page and return it as a html file.
#This month html files will contain the box scores of each game of the month.
#Keep in mind that, getting th e boxes scores of a currenty month can be tricy.
#This function needs to get the html file of the currently month everytime,
#because the html file of the currently month is updated every day, adding mors boxscores.
#This function will be called every day to get the updated html file of the currently month.

#SEASONS = [2018, 2019, 2020, 2021, 2022, 2023]
#checks just the current season if this is not the first time running the code
SEASONS = [2023]

# list all files in the current directory and prints them
print("Files in '%s': %s" % (os.getcwd(), os.listdir(os.getcwd())))

DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings') # data is a directory where standings will be located inside
SCORES_DIR = os.path.join(DATA_DIR, 'scores')

#currenty date
now = datetime.datetime.now()
#currenty month name in lower case
ACTUAL_MONTH = now.strftime("%B").lower()


def get_html(url, selector, sleep=7, retries=3): # async allow the code after it to imediatelly execute. 
    """ Info:
     This function will get the html content of a page and return it as a html file
      --------------------------------------------------------------------------------
       Input:
        url: url of the page to be scraped  
        selector: selector of the html element to be scraped
        sleep: time to wait between each try in seconds
        retries: number of tries to get the html content of each page
        --------------------------------------------------------------------------------
        Output:
        html: html content of the page
        """
    html=None
    for i in range(1, retries+1):
        time.sleep(sleep * i) # each try is longer by a sleep multiplication factor

        try:
            
            with sync_playwright() as p: # istance of playwright object. You may have to specify the path of the executable file of the browser you want to use.
                #executable_path= "C:/Users/Usuario/AppData/Local/ms-playwright/firefox-1369/firefox/firefox.exe"
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
    """ Info:
        This function will scrape the standings of a season and save them in a html file
        --------------------------------------------------------------------------------
        Input:
            season: season to be scraped
            --------------------------------------------------------------------------------
            Output:
            None
            """
    url  = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    
    
    html = get_html(url=url, selector='#content .filter')
    if html == None:
        print('still nothing on the first attempt to get the whole page content')
    else:
        print('attempt to get the whole page content succeds!')

        

    soup = BeautifulSoup(html, 'html.parser') #type: ignore
    links = soup.find_all('a')
    href = [l['href'] for l in links] # l is a hyperlink for a month
    stadings_pages = [f"https://www.basketball-reference.com{l}" for l in href]
#ok
    for url in stadings_pages: # navigate for each month page to save the file name first
        save_path = os.path.join(STANDINGS_DIR, url.split('/')[-1]) # saving in directory the name of the schedule month
        #print the save path
        print("save_path: ", save_path)

        #checking if the file already exists except for the current month that needs to be downloaded everytime
        if os.path.exists(save_path) and season != SEASONS[-1]: # if the file already exists and it is not the current season
            continue
        elif os.path.exists(save_path) and not re.search(ACTUAL_MONTH, save_path): # if the file already exists and it is the current season
            continue
        #So if is the current month and season, execute the scraping of the current month
        #
        #Deleting the current month file to get the updated version
        if os.path.exists(save_path) and re.search(ACTUAL_MONTH, save_path):
            os.remove(save_path)
            print(f'file {save_path} deleted')
        #grabbing table of month
        html = get_html(url=url, selector='#all_schedule')
        if html == None:
            print(f'still nothing on the first attempt to get the whole {url} content')
        else:
            print(f'attempt to get the {url} content succeds!')
        
        with open (save_path, 'w+') as f: # save_path is the name of the file that will be created (x is to create a new file to write)
            f.write(html) #type: ignore # content to be saved in the file  with specified name of save_path
    


#scrapping every season
for season in SEASONS:
    scrapy_season(season)
    print(f'scraped season {season} with success')

