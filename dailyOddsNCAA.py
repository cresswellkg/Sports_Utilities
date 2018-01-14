# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:21:54 2018

@author: Kelis
"""

from bs4 import BeautifulSoup
import re
import pandas as pd

def dailyOddsNCAA(day, month, year, odds_file, first_run = False):
    
    #Add leading zero to day & month to match sports book review url format
    
    if day < 10:
        day = str(0) + str(day)
    
    if month <10:
        month = str(0) + str(month)
    
    #Query page
    
    page = requests.get('https://www.sportsbookreview.com/betting-odds/ncaa-basketball/?date='+ str(year) + 
                        str(month) + str(day))

    soup = BeautifulSoup(page.content, 'html.parser')
    
    #Pull out links to lines 
    spread_links = soup.find_all('div', attrs={'rel':
        '1096'})
    
    spreads = [b.get_text() for b in spread_links]
    
    #Remove random xa0 that gets added to beginning
    
    del spreads[0]
    
    #Change pickems into 0s and make pattern match others
    
    spreads = [re.sub('PK', '0\xa0', x) for x in spreads]
    
    spreads = [x.split('\xa0', 1)[0] for x in spreads]
    
    #Loop through spreads and fill in every other value with opposite
    
    away_spread = list()
    home_spread = list()
    
    for spread in spreads:
        
        #Convert missing spreads to NA values
        if spread == '':
            spread = 'NA'
            away_spread.append(spread)
            home_spread.append(spread)
            continue
        
        #Convert ½ to .5 and convert to integer 

        spread = float(spread.replace('½', '.5'))
        
        #Since we only pull one spread (i.e +5) we mirror it so each team is assigned a value

        away_spread.append(spread)
        home_spread.append(-spread)
        
    
    ## Pulling out teams
    
    team_links = soup.find_all('span', attrs={'class':
        'team-name'})
    
    teams = [a.get_text() for a in team_links]
    
    #Remove the rankings from team names
    
    teams_new = list()
    for x in teams:
        
        #Find whether the team name can be split (means it has a ranking)
        if len(x.split('\xa0',1)) > 1:
            
            #Pull out team name using split if necessary
            teams_new.append(x.split('\xa0',1)[1])
            continue
        
        teams_new.append(x)
        
    #Place every other team into away and home arrays
    
    teams_away = teams_new[::2]
    teams_home = teams_new[1::2]
        
    #Getting overs
    
    page = requests.get('https://www.sportsbookreview.com/betting-odds/ncaa-basketball/totals/?date='+ str(year) + 
                        str(month) + str(day))

    soup = BeautifulSoup(page.content, 'html.parser')
    
    over_links = soup.find_all('div', attrs={'rel':
        '1096'})
    
    overs = [b.get_text() for b in over_links]
    
    #Since the html is identical just repeat everything from the spread section
    
    #Remove random xa0 that gets added to beginning
    
    del overs[0]
    
    #Remove unecessary characters
        
    overs = [x.split('\xa0', 1)[0] for x in overs]
    
    #Replace unicode ½ with .5
    
    overs = [o.replace('½', '.5') for o in overs]

    

    #Getting moneylines
    
    page = requests.get('https://www.sportsbookreview.com/betting-odds/ncaa-basketball/money-line/?date='+ str(year) + 
                        str(month) + str(day))

    soup = BeautifulSoup(page.content, 'html.parser')
    
    line_links = soup.find_all('div', attrs={'rel':
        '1096'})
    
    lines = [b.get_text(separator="x") for b in line_links]
        
    #Remove random xa0 that gets added to beginning
    
    del lines[0]
    
    #Loop through results and split by the added seperator x
    
    away_line = list()
    home_line = list()
                                   
    for line in lines:
        split_line = line.split('x',1)
        
        if len(split_line) == 1:
            away_line.append('NA')
            home_line.append('NA')
            continue
        
        away_line.append(split_line[0])
        home_line.append(split_line[1])

    
    #Get the date and make into a vector
    
    Date = str(month) + '/' + str(day) + '/' + str(year)
    
    Dates = np.repeat(Date, len(teams_home))
    
    #Accounting for rare case when theres a random gap due to early morning Hawaii game
    
    if len(overs) > len(teams_home):
        del home_spread[len(Dates)-1]
        del away_spread[len(Dates)-1]
        del home_line[len(Dates)-1]
        del away_line[len(Dates)-1]
        del overs[len(Dates)-1]

        
    
    #Combine everything
    
    
    results = pd.DataFrame({
            'Home' :teams_home, 
            'Away':teams_away, 
            'Date': Dates,
            'Home_Spread': home_spread, 
            'Away_Spread': away_spread, 
            'Home_ML': home_line, 
            'Away_ML': away_line, 
            'Over': overs}, columns = ['Home',
    'Away', 'Date', 'Home_Spread', 'Away_Spread',
    'Home_ML', 'Away_ML', 'Over'])
    
    if first_run:
        header = True
    else:
        header = False
        
    results.to_csv(odds_file, mode = 'a', header = header, index = False)

    

#Code to get today's odds 

#import datetime
#import os

#os.chdir("C:\\Users\\Kelis\\Documents\\Sports_Utilities")
#day = datetime.datetime.now().day
#month = datetime.datetime.now().month
#year = datetime.datetime.now().year
#odds_file = "odds.csv"
#first_run = True

#dailyOddsNCAA(day,month,year,odds_file,first_run)
    
