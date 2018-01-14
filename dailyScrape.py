# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 17:52:59 2018

@author: Kelis
"""

from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np
from datetime import datetime

def DailyScrape(day, month, year, box_file):

    overres = np.empty((0,51))
    
    #For each day pull out the url of the page with all box scores

    page = requests.get('http://www.sports-reference.com/cbb/boxscores/index.cgi?month=' + str(month) + '&day=' + str(day) + ' &year='+ str(year))
    soup = BeautifulSoup(page.content, 'html.parser')
    
    #Pull out just the ending of each the url of each game on the given day
    
    final_links = soup.find_all('td', {'class': 'right gamelink'})
    final_links = list(final_links)
    links = list()   
    for l in final_links:
        links.append(l.a["href"])
    
    #Loop through each individual game and pull out box scores
    
       
    for m in links:
        
        #Naviagate to a given link
        page = requests.get('http://www.sports-reference.com/'+str(m))
        soup = BeautifulSoup(page.content, 'html.parser')  
        
        
        
        #Pull out the teams playing on the day
        
        teams = soup.find_all('a', {'itemprop': 'name'})
        results = np.empty((0,0))
        for team in teams: results = np.append(results, team.string)
                        
        #Extract one table to obtain headers
        basictab = soup.find('table', {"class": "sortable"} )
        columnName = [item['data-stat'] for item in basictab.find_all(attrs={'data-stat' : True})]
        columnName = pd.unique(columnName)
        
        #Use minutes as an indication of when one team's stats end. Minutes equaling 200 or more indicates the final position
        
        minutes = soup.find_all('td',attrs={'data-stat' : str(columnName[2])})
        
        rawminutes = list()
        for n in range(0,len(minutes)-1): 
            rawminutes.append(int(minutes[n].text.strip()))
        rawminutes = np.asarray(rawminutes)
        
        #Find the location of the end of each minutes count to parse minutes by team
        
        endteam1 = np.where(rawminutes >= 200)
        
        if not endteam1[0]:
            continue
        endteam1 = endteam1[0][0]
    
        #Begin loop which pulls out stats for a given game
        
        for cName in columnName[2:] :
            stat = soup.find_all('td',attrs={'data-stat' : str(cName)})
            results = np.append(results,stat[endteam1].text.strip())
            results = np.append(results,stat[len(stat)-1].text.strip())
            
        #Identify the number of occurences of each team and keep a count
        
        tot_teams = np.vstack([overres[:,[0]], overres[:,[1]]])
    
        for index in range(0,2): 
            teamcount = np.count_nonzero(tot_teams == str(results[index]))+1   
            results = np.append(results,teamcount)
         
        #Append results to an overall list of the days results
        
        #Add day, month and year to the results matrix
        
        results = np.append(results,day)
        results = np.append(results,month)
        results = np.append(results,year)
        results = np.matrix(results)
        overres = np.vstack([overres, results])
            
        box_score = pd.DataFrame(overres)
        box_score.to_csv(box_file, mode = 'a', header = False)

day = datetime.now().day-1
month = datetime.now().month
year = datetime.now().year
box_file = "box_scores.csv"

DailyScrape(day, month, year, box_file)


