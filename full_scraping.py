#############################################################################################
#WEB SCRAPING: NOTEBOOK 1 - GETTING STANDINGS PAGES
#############################################################################################
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



DATA_DIR = os.path.join('Web Scraping', 'data') # data is a directory where standings will be located inside
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



#############################################################################################
# WEB SCRAPING: NOTEBOOK 2 - GETTING BOX SCORES
#############################################################################################
from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright, TimeoutError as playwrightTimeout
import time
import datetime
import os, sys, shutil, gzip
import zlib
import zipfile
from tqdm import tqdm
import re



STANDINGS_DIR = os.path.join(DATA_DIR, 'standings') # data is a directory where standings will be located inside
SCORES_DIR = os.path.join(DATA_DIR, 'scores')
ACTUAL_MONTH_SCORES_DIR = os.path.join(DATA_DIR, 'actual_month_scores') # data is a directory where standings will be located inside
#SEASONS 
SEASONS = [2023]


#Dealing with months transition, as our objective is to mantain th e data of the actual month separated from the rest of the data
#But also, when the actual month changes, we want to pass all the data of the previous month to the compressed_games.zip file,
# moving it from the actual_month_scores directory to the scores directory.
#get actual month and year strings using datetime library
now = datetime.datetime.now()
ACTUAL_MONTH = str(now.month).zfill(2) # zfill is a method that adds a 0 to the left of the string if it has only one digit
# getting the name of the actual month in lower case
ACTUAL_MONTH_NAME = now.strftime("%B").lower()
#ACTUAL_YEAR = str(now.year)
print(f'actual month: {ACTUAL_MONTH}, actual year: {now.year}, actual day: {now.day}')
#checking if it is the first day of the month, which means that we have to move the data of the previous month to the compressed_games.zip file
# if it is the first day of the month
    #we have to move the data of the previous month to the compressed_games.zip file
# also, if it is day 1, we can decompress the compressed_games.zip file, and put it together with previous month data, to then compress it again all together.

#day = 0 Set this if you want to scrape all the data ( like if you are running the code for the first time)

#note: if is the first time running the app, the application will have to run as if is day 1, so we get all past years data properly. As it is, we just gether the actual month data
#day = 1
day = now.day
if day == 1:
        print(f'Today is the first {day} of the month, so we have to move the data of the previous month to the compressed_games.zip file')
        if os.path.exists(DATA_DIR+'compressed_games.zip'): # if the compressed_games.zip file exists
        #decompressing the compressed_games.zip file to the scores directory
            with zipfile.ZipFile(os.path.join(SCORES_DIR, 'compressed_games.zip'), 'r') as zip_ref:
                zip_ref.extractall(SCORES_DIR)
        #we have to move the data of the previous month to the compressed_games.zip file
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

    soup = BeautifulSoup(html, 'html.parser' )
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
#if the day is the first of the month, we will have th edecompressed past files, so this function will try to scrape them all, but 
# it also checks if the file exists,  so we dont scrape the same file twice. Is usefull if we have nothing, we just set the day to 1 and run the script
# also needed to join previous data with this past data
if day == 1:
    print('Scraping the box scores of the past seasons, this is the first time we run our code or is day 1.')
    standing_file_names = os.listdir(STANDINGS_DIR) # list of our filename of standings
    #filtering just elements we want
    standing_file_names = [file for file in standing_file_names if '.html' in file]
    #creating the paths names and the scraping, for each season
    for season_year in SEASONS :
        print(f'Scraping the box scores of the {season_year} season')
        season_files = [file for file in standing_file_names if str(season_year) in file]
        for file in season_files: 
            file_path = os.path.join(STANDINGS_DIR, file)
            scrape_boxscores(file_path, season_year=season_year)

print('Scraping the box scores of the actual month of the current season')
#scraping the actual month, same code as before, but we are only scraping the actual month
standing_file_names = os.listdir(STANDINGS_DIR) # list of our filename of standings
#filtering just elements we want ( in this case, just the actual month of the currenty season)
#taking only the current season, and the actual month file of standing_file_names

standing_file_name_actual = [file for file in standing_file_names if str(SEASONS[-1]) in file and ACTUAL_MONTH_NAME in file]


print(f'Standings files: {standing_file_name_actual}')
#creating the paths names and the scraping, for each season

file_path = os.path.join(STANDINGS_DIR, standing_file_name_actual[0])
scrape_boxscores(file_path, season_year=SEASONS[-1])




#compressing the files in the scores directory (except the actual month), if is day 1
#and saving the compressed file in the data directory
#day means that there are past files to compress, or past files + prevoius month to compress
if day == 1:
    print(f'Today is day {day}, Compressing the past files in the compressed_games.zip file, then removing it from the scores directory')
    file_names = os.listdir(SCORES_DIR)
    file_names = [file for file in file_names if '.html' in file]
    output_path = DATA_DIR
    compress(file_names, SCORES_DIR, output_path)

    #excluding the html files from the past data that was compressed in the compressed_games.zip file
    #deleting files

    box_scores = [file for file in os.listdir(SCORES_DIR) if '.html' in file]
    for file in tqdm(box_scores):
        os.remove(os.path.join(SCORES_DIR, file))
print('All html past files deleted')
print("Automated scraping and files organization finished!")


############################################################################################################
#WEB SCRAPING: NOTEBOOK 03 - PARSING DATA TO NBA DATABASE
############################################################################################################




import os 
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import date
from tqdm import tqdm
import sqlalchemy
import pickle


    

pd.set_option('mode.chained_assignment', None)



#setting our directoys paths

SCORE_DIR = os.path.join(DATA_DIR, 'scores')
SCORE_DIR_ACTUAL = os.path.join(DATA_DIR, 'actual_month_scores')

def clean_html(box_score):
    """ Info:
        This function will clean the html file and return a soup object
        ---------------------------------------------------------------
        Input:
        box_score: html file
        ---------------------------------------------------------------
        Output:
        soup: BeautifulSoup object
        """
    
    with open(box_score, 'r', encoding="utf-8", errors='ignore') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    [f.decompose() for f in soup.select('tr.over_header')]
    [f.decompose() for f in soup.select('tr.thead')]
   

    return soup

def get_score_line(soup):
    """ Info:
        This function will get the score line from the soup object
        and return a dataframe with the score line.
        ---------------------------------------------------------------
        Input:
        soup: BeautifulSoup object
        ---------------------------------------------------------------
        Output:
        score_row: Dataframe with the score line of the game with total points.  """

    score_row = pd.read_html(str(soup), attrs={'id': 'line_score'})[0] # grab the first table, thats actually the table we want
    # we get to change name of first column and last column (total and teams names) because colunns dinamically change in between
    score_row.columns.values[0] = 'Team' # first column with the teams name
    score_row.columns.values[-1] = 'Total' # switch name of T for Total
    score_row = score_row[['Team', 'Total']] # we get only the important values for us, and ignore the partial scores.

    return score_row

#Now, we gonna create a function to grab the basic and advanced stats by team, in a list of the 2 teams that are playing each other
def get_stats(soup, team, stat):
    """ Info:
        This function will get the stats from the soup object
        and return a dataframe with the stats.
        ---------------------------------------------------------------
        Input:
        soup: BeautifulSoup object
        team: string with the team name
        stat: string with the type of stats (basic or advanced)
        ---------------------------------------------------------------
        Output:
        df: Dataframe with the stats of the game.  """
    
    df = pd.read_html(str(soup), attrs={'id':f'box-{team}-game-{stat}'}, index_col=0)[0] # indexcol will be the players column
    
    df = df.apply(pd.to_numeric, errors='coerce')
    return df



#Function to get the season of that game.
def get_game_season(soup):
    """ Info:
        This function will get the season of the game from the soup object
        and return a string with the season.
        ---------------------------------------------------------------
        Input:
        soup: BeautifulSoup object
        ---------------------------------------------------------------
        Output:
        string: string with the season of the game.  """
    id = soup.select('#bottom_nav_container')[0]
    string= id.find_all('u')[3] # this u tag has the exact season, so we use regex to extract it
    return re.findall(r'\d{4}-\d{2}', str(string))[0]


#Getting the names of or downloaded boxscore in a list if it is the first time running the code

first_time = False

#first, we decompress the compressed_games.zip file
if first_time:
    with zipfile.ZipFile(os.path.join(DATA_DIR, 'compressed_games.zip'), 'r') as zip_ref:
        zip_ref.extractall(SCORE_DIR)

    #then, we get the names of the files in the directory
    box_scores_old = os.listdir(SCORE_DIR)

    # joining the names of the boxscores with ther directory to a list of html files
    box_scores_old = [os.path.join(SCORE_DIR, file) for file in box_scores_old if file.endswith('.html')] # file names

    print(f'we have {len(box_scores_old)} games scraped')

    games_scores = box_scores_old


box_scores = os.listdir(SCORE_DIR_ACTUAL)

# joining the names of the boxscores with ther directory
box_scores = [os.path.join(SCORE_DIR_ACTUAL, file) for file in box_scores if file.endswith('.html')] # file names

print(f'we have {len(box_scores)} games scraped')


games_scores = box_scores

if 'games_ids.pkl' not in os.listdir('Web Scraping'):
    games_ids = []
else:
    games_ids = pickle.load(open(os.path.join('Web Scraping', 'games_ids.pkl'), 'rb'))

base_cols = None
games = []
count = 0 # coounting the number of corrupted html files

for box_score in tqdm(games_scores): # tqm to track progress.
    # we get the name of the file, and we check if it was already parsed
    game_file_name = os.path.basename(box_score)

    if game_file_name in games_ids: # if this data was aready grabbed of the box downloaded, go to next
        print(f'{game_file_name} already parsed!')
        continue

    
    try:  # if html is somewaht corrupted, we go to the next
        soup = clean_html(box_score)
        score_row = get_score_line(soup)
        
        all_stats = [] # this is resposible to store data from both teams

        for team in score_row['Team']:
            
            # we do not need the +/- and BPM columns, as they are not present in totals of the team standings
            basic_df = get_stats(soup, team, 'basic')      
            advanced_df = get_stats(soup, team, 'advanced')
            

            # we only need the totals row of the stats table, and we need to concatenated both basic and advanced table
            totals = pd.concat([basic_df.iloc[-1], advanced_df.iloc[-1]], axis=0)# concat 2 series
            totals.index = totals.index.str.lower()
            
            
            

            # getting also the coluns of te max individual stat per player, so we exclude totals. This line , maxes, is optional.
            maxes = pd.concat([basic_df.iloc[:-1].max(), advanced_df.iloc[:-1].max()], axis=0)
            maxes.index =  maxes.index.str.lower() + '_max' 

            stats = pd.concat([totals, maxes], axis=0)
            

            #some tables do not have the same rows, with a variable named bpm, and duplicates, so we gonna deal with

            if base_cols is None:
                base_cols = list(stats.index.drop_duplicates(keep='first'))
                base_cols = [col for col in base_cols if 'bpm' not in col]

            stats = stats[base_cols]

            # append for both teams

            all_stats.append(stats)

        stats = pd.concat(all_stats, axis=1).T # stacking rows of teams

        # combining the score row with stats to get the points and the name of the team
        game_stats = pd.concat([stats, score_row], axis=1) # stacking columns of dfs
        game_stats['season'] = get_game_season(soup)

        # getting just the date of the file name
        
        game_stats['date'] = pd.to_datetime(game_file_name[:8])
        
        

        game_stats['home'] = [0, 1]  # as the home team is always second in the list, we just index this way
        
        game_stats_opponent = game_stats.iloc[::-1].reset_index() # let us concatenate later
        game_stats_opponent.columns = 'opponent_' + game_stats_opponent.columns 

        

        full_game_stats = pd.concat([game_stats, game_stats_opponent], axis=1)
        full_game_stats['ID'] = game_file_name
        full_game_stats['WIN'] = full_game_stats['Total'] > full_game_stats['opponent_Total'] #adding the target column WIN (1) or LOSS (0)

        games.append(full_game_stats)
        games_ids.append(game_file_name) # appending the game unique file name

        
    except:
        count += 1
        print(f'Number of corrupted boxes: {count}')
        print(f'Corrupted box: {game_file_name}')
        continue

from sqlalchemy import create_engine, text
   

nba_games_db_path = os.path.join('Web Scraping', 'nba_games.db')
# creating a database
engine = sqlalchemy.create_engine('sqlite:///' + nba_games_db_path, echo=False, pool_pre_ping=True)
print('engine created!')
#reading the database to a dataframe
query = 'SELECT * FROM nba_games'
df_allgames = pd.read_sql(sql=text(query), con=engine.connect())

# saving our parsed games in a dataframe 
if games: 
    df_games = pd.concat(games, axis=0, ignore_index=True) # stack rows of games, assuming all dfs have the same columns
    #trating df_games to have the same columns as df_allgames
    df_games = df_games[df_allgames.columns]

    

    # saving to database
    df_games.to_sql('nba_games', con=engine, if_exists='append', index=False)
    #saving games new ids into a file
    pickle.dump(games_ids, open(os.path.join('Web Scraping', 'games_ids.pkl'), 'wb'))
    print('new games added!')
else:
    print('no new games added!')


# reading from database
df_allgames = pd.read_sql(sql=text(query), con=engine.connect())


#deleting the extracted html files as we already saved them in a list as objects, in the past data scores directory
html_files = [file for file in os.listdir(SCORE_DIR) if file.endswith('.html')]
for file in tqdm(html_files):
    os.remove(os.path.join(SCORE_DIR, file))
print('All html past files deleted')



############################################################################################################
# DATA ANALISYS: NOTEBOOK 01 - DATA CLEANING TO PRODUCTION DF
############################################################################################################


#--------Utilities--------#
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlalchemy
import warnings
import os



#--------Settings--------#
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option('mode.chained_assignment', None)
pd.set_option('display.max_columns', None)



#--------Data--------#


engine = sqlalchemy.create_engine('sqlite:///' + nba_games_db_path)

df = df_allgames.copy()


df = df.loc[:, df.columns != 'ID'] #type: ignore


df = df.drop_duplicates(keep='first')

print('outliers porcentage: {:.2%}'.format(len(df[df['mp'] != 240])/len(df)))

 #deleting outliers rows   
df = df[df['mp'] == 240]
df.shape


def del_cols(df, cols):
    """ Info:
        This function deletes the columns that are not needed for the analysis.
         It will first check to see if it exists in the dataframe, and if it does, it will delete it.
         -------------------------------------------------------------------------------------------
        Input:
          df: dataframe
           cols: list of columns to be deleted
         -------------------------------------------------------------------------------------------
        Output:
            df: dataframe without the columns that were deleted """
    col_list = []
    for col in cols:
        if col in df.columns:
            col_list.append(col)

    df.drop(col_list, axis=1, inplace=True)
    return df


del_list = ['mp','mp.1','+/-','mp_max','mp_max.1',
 'opponent_index','opponent_mp',
 'opponent_mp.1','opponent_+/-','opponent_mp_max.1', 'opponent_mp_max',
   'opponent_date', 'opponent_season', 'opponent_home']


df = del_cols(df, del_list)


#saving the dataframe to pickle file
df.to_pickle('production_df.pkl')
#printing the last game date, based on the last row of the dataframe
print('Last game date: {}'.format(df['date'].iloc[-1].strftime('%Y-%m-%d')))
print('Dataframe saved to pickle file, our production dataframe is ready to be used to generate new predictions!')


