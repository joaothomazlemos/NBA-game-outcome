from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time
import datetime
import os, sys, shutil, gzip
import zlib
import zipfile
from tqdm import tqdm
from IPython.display import clear_output
import re


DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings') # data is a directory where standings will be located inside
SCORES_DIR = os.path.join(DATA_DIR, 'scores')
ACTUAL_MONTH_SCORES_DIR = os.path.join(DATA_DIR, 'actual_month_scores') # data is a directory where standings will be located inside
#SEASONS = list(range(2016, 2023))
SEASONS = [2018, 2019, 2020, 2021, 2022, 2023]


#Dealing with months transition, as our objective is to mantain th e data of the actual month separated from the rest of the data
#But also, when the actual month changes, we want to pass all the data of the previous month to the compressed_games.zip file,
# moving it from the actual_month_scores directory to the scores directory.
#get actual month and year strings using datetime library
now = datetime.datetime.now()
ACTUAL_MONTH = str(now.month).zfill(2) # zfill is a method that adds a 0 to the left of the string if it has only one digit
#ACTUAL_YEAR = str(now.year)

#checking if it is the first day of the month, which means that we have to move the data of the previous month to the compressed_games.zip file
# if it is the first day of the month
    #we have to move the data of the previous month to the compressed_games.zip file
 
if now.day == 1:
        for file in os.listdir(ACTUAL_MONTH_SCORES_DIR):
            shutil.move(os.path.join(ACTUAL_MONTH_SCORES_DIR, file), os.path.join(SCORES_DIR, file)) 




def compress(file_names, files_path, output_path):


    '''
    Info:
        Compresses files in the path with the names in the list.
    ----------
    Input:
        file_names: list of file names to compress (type: list)
        files_path: path to the files to compress (type: str)
        output_path: path to the output file (type: str)
    ----------
    Output:
        Compressed files in the path with the names in the list, as compressed_games.zip.
    '''
     
    print('Compressing files...')

    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED

    # create the zip file first parameter path/name, second mode
    zf = zipfile.ZipFile(os.path.join(output_path, 'compressed_games.zip'), mode="w")
    try:
        for file_name in tqdm(file_names):
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            zf.write(os.path.join(files_path, file_name), file_name, compress_type=compression)

    except FileNotFoundError:
        print(f"An error occurred, file {os.path.join(files_path, file_name)} not found") #type: ignore
    finally:
        # Close the zip file to create a fulll compressed object
        zf.close()


def get_html(url, selector, sleep=7, retries=3): # async allow the code after it to imediatelly execute. 
    """ 
    Info:
        Gets the html of a url.
        ----------------------
         Input:
            url: url to get the html from (type: str)
             selector: selector of the html to get (type: str)
              sleep: time to sleep between retries (type: int)
               retries: number of retries (type: int)
                ----------------------------------------
                 Output:
                    html: html page of the url (type: str) """

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

def scrape_boxscores(standing_file, season_year): # getting the paths of the htmls
    """ 
     Info:
        Gets the box scores of a month and saves it. We want to save all data in a directory,
        and the data of the actual month in a different directory, to deal with incoming real time data.
          Because the domain uses a single year to a single season that actually takes two years,
          we have to deal with the transition between seasons.
          For this, we are only saving the data of the actual month in the actual_month_scores directory, when
          the month == current month, and the year == the last year of the seasons list.
         --------------------------------
          Input:
             standing_file: path to the standings file (type: str)
              Example: 'data/standings/NBA_2022_games-june.html'
                season_year: year of the season (type: int)
               ----------------------------------------
                Output:
                   box_scores: list of box scores (type: list)
                     """
     # here we grab a month and go trough all the month box scores
    with open(standing_file,'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    hrefs = [l.get('href') for l in links]
    box_scores = [href for href in hrefs if href and 'boxscore' in href and '.html' in href]
    box_scores = [f'https://www.basketball-reference.com/{href}' for href in box_scores ]
    #now we have all the links of the box , of all box of the months, of all months together ordered chronologically
    print(f'Now scraping the box scores of the {standing_file.split("/")[-1]}')

    for url in tqdm(box_scores): # navigate for each month page to save the file name first
            #if the file is from the actual month, its only saved on the actual month directory.
            #if does not exist, we can scrap and save it. For this to work,
            #we have to assume that the actual month is the last one in the list of box_scores
            #and is not in scores directory by some mistake

            #using regex to check if the url contains the actual month and year concatenated
            pattern = re.compile(f'{season_year}{ACTUAL_MONTH}')

            if re.search(pattern, url) and season_year == SEASONS[-1]: # if the url contains the actual month and year concatenated
                save_path = os.path.join(ACTUAL_MONTH_SCORES_DIR, url.split('/')[-1])
              
            else:
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
            
            #We are going to save the all the hmtl files in on directory, except the content of the actual month
            #This is because we are going to update the actual month every day, so dont need to compress it in th ecompressed_games.zip file.
            #We are going to save the actual month in a different directory, and we are going to compress it in a different zip file.
            
            with open (save_path, 'w+', encoding="utf-8") as f:
                f.write(html) # content to be saved in the file  with specified name

#STARTING TO GRAB OUR DATA

standing_file_names = os.listdir(STANDINGS_DIR) # list of our filename of stanfdings
#filtering just elements we want
standing_file_names = [file for file in standing_file_names if '.html' in file]
#creating the paths names and the scraping, for each season
for season_year in SEASONS :
    print(f'Scraping the box scores of the {season_year} season')
    season_files = [file for file in standing_file_names if str(season_year) in file]
    for file in season_files: 
        file_path = os.path.join(STANDINGS_DIR, file)
        scrape_boxscores(file_path, season_year=season_year)


#decompressing all files of the compressed_games.zip file in the scores directory 
# if the compressed file exists and it is the first day of the month, where
# we are going to take the data of the previous month and join with all our past data
if os.path.exists(DATA_DIR+'compressed_games.zip') and now.day == 1:
    with zipfile.ZipFile(DATA_DIR+'compressed_games.zip', 'r') as zip_ref:
        zip_ref.extractall(SCORES_DIR)


#compressing the files in the scores directory (except the actual month)
#and saving the compressed file in the data directory
file_names = os.listdir(SCORES_DIR)
file_names = [file for file in file_names if '.html' in file]
output_path = DATA_DIR
compress(file_names, SCORES_DIR, output_path)

#excluding the html files from the past data that was compressed in the compressed_games.zip file
#deleting files

box_scores = os.listdir(SCORES_DIR)
for file in tqdm(box_scores):
    os.remove(os.path.join(SCORES_DIR, file))
print('All html past files deleted')
print("Automated scraping and files organization finished!")






