# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 00:05:51 2018

@author: cresswellkg
"""

from bs4 import BeautifulSoup
import lxml
import pandas as pd
import requests
import numpy as np
from datetime import datetime
import re

page = requests.get('https://www.pro-football-reference.com/years/' + str(year) + '/games.htm')
soup = BeautifulSoup(page.content, 'html.parser')

#Pull out just the ending of each the url of each game on the given day

#Get all links

boxscores = soup.find_all('td', {'data-stat': 'boxscore_word'})
weeks = soup.find_all('th', {'class': 'right', 'data-stat': 'week_num'})

#Get the actual week label

week = list()

for w in weeks:
    try:
        week.append(w.text)
    except Exception:
        next

#Filtering out empty weeks

week = list(filter(None, week))
        
boxscores = list(boxscores)
links = list()   
for l in boxscores:
    links.append(l.a["href"])


for l in links:
    
    curr_game_page = requests.get('https://www.pro-football-reference.com' + l)
    soup = BeautifulSoup(curr_game_page.content, 'html.parser')
    
    #Pull out the table of offensive stats after fixing issue with commented out table
    
    stats_html = soup.find(string=re.compile('id="player_offense"'))
    stats_soup = BeautifulSoup(stats_html, "html.parser")
    
    #Grab table and create data frame from it
    
    off_tab = stats_soup.find_all('table')[0]
    
    df = pd.read_html(str(off_tab))[0]    
    
    #Manually create list of column names and apply to data frame
    
    colnames = ["Player", "Team", "Completions", "Attempts", "Passing Yards", "Passing TDs", "Interceptions", "Sacks", "Yards Sacked", "Longest Pass", "QB Rating", "Rushing Attempts", "Rushing Yards", "Rushing TDs","Longest Rush", "Targets", "Catches",  "Receiving Yards", "Receiving TDs", "Longest Catch", "Fumbles", "Fumbles Lost"]
    
    df.columns = colnames
    
    #Removing unneeded rows
    
    #Find the middle row with random labels by finding the row where player is nan
    
    middle_col = np.where(df['Player'].isnull())
    
    df.drop(df.index[[middle_col[0][0],middle_col[0][0]+1]], inplace=True)

    