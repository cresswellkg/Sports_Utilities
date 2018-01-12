from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re
import csv
import os


#Specify the starting and ending date to pull box scores
def BoxScoreScrape(start_year, end_year, months, start_day, end_day):
    years = [start_year, end_year]
#    months = [start_month,end_month]
    days = range(start_day, end_day)
    
    final = np.empty((0,51))
    overres = np.empty((0,51))
    for year in years:
        for month in months:
            for day in days:
                
                if month == 4 and day >3:
                    break
                
                #For each day pull out the url of the page with all box scores
                
                try:
                    page = requests.get('http://www.sports-reference.com/cbb/boxscores/index.cgi?month=' + str(month) + '&day=' + str(day) + ' &year='+ str(year))
                except Exception:
                    continue
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
                    try:
                        page = requests.get('http://www.sports-reference.com/'+str(m))
                    except Exception:
                        continue
                    soup = BeautifulSoup(page.content, 'html.parser')  
                    
                    
                    
                    #Pull out the teams playing on the day
                    try:
                        teams = soup.find_all('a', {'itemprop': 'name'})
                    except Exception:
                        continue
                    results = np.empty((0,0))
                    for team in teams: results = np.append(results, team.string)
                                
                    html = list(soup.children)[2]
    
                    #Extract one table to obtain headers
                    basictab = soup.find('table', {"class": "sortable"} )
                    try:
                        columnName = [item['data-stat'] for item in basictab.find_all(attrs={'data-stat' : True})]
                    except Exception:
                        continue
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
                    
                status_check = pd.DataFrame(overres)
                status_check.to_csv("box_scores.csv")

        
start_year = 2017
end_year = 2018
start_day = 1
end_day = 32
months = [11,12,1]

BoxScoreScrape(start_year, end_year, months, start_day, end_day)
