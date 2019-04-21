# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 13:24:42 2018

@author: cresswellkg
"""

import bs4
from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np
import os
from datetime import datetime

#os.chdir("C:\\Users\\cresswellkg\\Documents\\Sports_Utilities")

#Function for converting XX:XX time to seconds

def time2secs(x):
    minutes = int(x[0:2])*60
    seconds = int(x[3:5])
    return minutes+seconds

def scrapeTrips(day, month, year, box_file, first_run = True):
    
    #For each day pull out the url of the page with all box scores
    
    page = requests.get('http://www.sports-reference.com/cbb/boxscores/index.cgi?month=' + str(month) + '&day=' + str(day) + ' &year='+ str(year))
    soup = BeautifulSoup(page.content, 'html.parser')
    
    #Pull out just the ending of each url and augment to be play by play
    
    final_links = soup.find_all('td', {'class': 'right gamelink'})
    final_links = list(final_links)
    links = list()   
    for l in final_links:
        l = l.a["href"]
        l_split = l.split("/")
        l = l_split[1] + "/" + l_split[2] + "/" + "pbp/" + l_split[3]
        links.append(l)
        
    for m in links:
            
        #Naviagate to a given link
        over_res = pd.DataFrame()

        try:
            page = requests.get('http://www.sports-reference.com/'+str(m))
            soup = BeautifulSoup(page.content, 'html.parser')  
        
            #Pull out the teams playing on the day
            
            teams = soup.find_all('a', {'itemprop': 'name'})
            results = np.empty((0,0))
            for team in teams: results = np.append(results, team.string)
            
            #Test if its backwards and skip if so
            
            start_score = soup.find_all('td', {'data-stat': 'score'})[0].get_text()
            
            if ((start_score != "0-0") and (start_score != "2-0") and 
            (start_score != "0-2") and (start_score != "3-0") and
            (start_score != "0-3")):
                next
            #Pull out plays for both teams
            
            
            visitor_plays = soup.find_all('td', {'data-stat': 'visitor_play'})
            visitor_plays = [plays.get_text() for plays in visitor_plays]
            
            home_plays = soup.find_all('td', {'data-stat': 'home_play'})
            home_plays = [plays.get_text() for plays in home_plays]
            
            visitor_time = soup.find_all('th', {'data-stat': 'time_remaining'})
            visitor_time = [sec.get_text() for sec in visitor_time]
            visitor_time = [x for x in visitor_time if "Time" not in x]
            
            home_time = visitor_time
                
            
            #Visitor time until shot
            
            i = 0
            visitor_event = []
            while i <(len(visitor_plays)-1):
                if ("defensive rebound" in visitor_plays[i] or
                "steal" in visitor_plays[i] or
                "timeout" in visitor_plays[i] or
                "substitution" in visitor_plays[i]) and ("makes" in visitor_plays[i+1] or
                "misses" in visitor_plays[i+1] or "block" in visitor_plays[i+1]):
                    time_elapsed = time2secs(visitor_time[i])-time2secs(visitor_time[i+1])
                    visitor_event.append(time_elapsed)
                    i = i+2
                elif ("assist" in home_plays[i] or
                "substitution" in home_plays[i] or
                "turnover" in home_plays[i] or
                "makes" in home_plays[i] or
                "misses" in home_plays[i]) and ("makes" in visitor_plays[i+1] or
                "misses" in visitor_plays[i+1] or "block" in visitor_plays[i+1]):
                    time_elapsed = time2secs(home_time[i])-time2secs(visitor_time[i+1])
                    visitor_event.append(time_elapsed)
                    i = i+2
                else:
                    i = i+1
                    
            visitor_event = [s for s in visitor_event if s > 0]
            
            #Home time until shot
            
            i = 0
            home_event = []
            while i <(len(home_plays)-1):
                if ("defensive rebound" in home_plays[i] or
                "steal" in home_plays[i] or
                "timeout" in home_plays[i] or
                "substitution" in home_plays[i]) and ("makes" in home_plays[i+1] or
                "misses" in home_plays[i+1] or "block" in home_plays[i+1]):
                    time_elapsed = time2secs(home_time[i])-time2secs(home_time[i+1])
                    home_event.append(time_elapsed)
                    i = i+2
                elif ("assist" in visitor_plays[i] or
                "substitution" in visitor_plays[i] or
                "turnover" in visitor_plays[i] or
                "makes" in visitor_plays[i] or
                "misses" in visitor_plays[i]) and ("makes" in home_plays[i+1] or
                "misses" in home_plays[i+1] or "block" in home_plays[i+1]):
                    time_elapsed = time2secs(home_time[i])-time2secs(home_time[i+1])
                    home_event.append(time_elapsed)
                    i = i+2
                else:
                    i = i+1
                    
            home_event = [s for s in home_event if s > 0]
            
        
            
            #Identify free throws
            
            visitor_ft = ["free throw" in plays for plays in visitor_plays]
            home_ft = ["free throw" in plays for plays in home_plays]
            
            #Identify plays with a made shot
            
            visitor_made = ["makes" in plays for plays in visitor_plays] 
            home_made = ["makes" in plays for plays in home_plays] 
            
            #Identifying total offensive rebounds (To take into account team offensive rebounds)
            
            visitor_orb = ["offensive rebound" in plays for plays in visitor_plays]
            home_orb = ["offensive rebound" in plays for plays in home_plays]
            
            #Identifying total turnovers (To take into account team turnovers)
            
            visitor_tov = ["turnover" in plays for plays in visitor_plays]
            home_tov = ["turnover" in plays for plays in home_plays]
            
            #Identify non-play events (timeouts, substitutions and deadball rebounds) that can come between free throws
            
            visitor_np = ["assist" in plays or "foul" in plays or "timeout" in plays or "substitution" in plays or "deadball rebound" in plays for plays in visitor_plays]
            home_np = ["assist" in plays or "foul" in plays or "timeout" in plays or "substitution" in plays or "deadball rebound" in plays  in plays for plays in home_plays]

            #Ignore these values in all other lists
            
            visitor_ft = [x for i,x in enumerate(visitor_ft) if (visitor_np[i]==False) & (home_np[i] == False)]
            visitor_made = [x for i,x in enumerate(visitor_made) if (visitor_np[i]==False) & (home_np[i] == False)]

            home_ft = [x for i,x in enumerate(home_ft) if (visitor_np[i]==False) & (home_np[i] == False)]
            home_made = [x for i,x in enumerate(home_made) if (visitor_np[i]==False) & (home_np[i] == False)]
            
            #Filter out free throw makes from all other makes
            
            visitor_made = [(visitor_ft[i] == False) & (visitor_made[i] == True) for i in range(0, len(visitor_made))]
            home_made = [(home_ft[i] == False) & (home_made[i] == True) for i in range(0, len(home_made))]
            
            if (start_score != '0-0') & (start_score != '0-2') & (start_score != '2-0') & (start_score != '3-0') & (start_score != '0-3'):
                visitor_ft.reverse()
                home_ft.reverse()
                visitor_made.reverse()
                home_made.reverse()
                
                
            #Loop through free throws and change name based on the type
            i = 0
            while i < (len(visitor_ft)-1):
                
                if visitor_ft[i] == False:
                    i = i+1
                elif (visitor_ft[i+1] == False) & (visitor_made[i-1] == False):
                    visitor_ft[i] = "1Shot"
                    i = i+1
                elif (visitor_ft[i+1] == True) & (visitor_ft[i+2] == False) & (visitor_made[i-1] == False):
                    visitor_ft[i] = "2Shot"
                    i = i+2
                elif (visitor_ft[i+1] == True) & (visitor_ft[i+2] == True) & (visitor_made[i-1] == False):
                    visitor_ft[i] = "3shot"
                    i = i+3
                else:
                    visitor_ft[i]  = "And1"
                    i = i+1
                    
            results_visit = [visitor_ft.count("1Shot"), visitor_ft.count("2Shot"), visitor_ft.count("3shot"), 
                            visitor_ft.count("And1"), visitor_orb.count(True), visitor_tov.count(True), 
                            np.min(visitor_event), np.max(visitor_event), np.mean(visitor_event),
                            np.median(visitor_event), np.std(visitor_event)]            
            #Repeat for home team
            
            i = 0
            while i < (len(home_ft)-1):
                
                if home_ft[i] == False:
                    i = i+1
                elif (home_ft[i+1] == False) & (home_made[i-2] == True):
                    home_ft[i] = "1Shot"
                    i = i+1
                elif (home_ft[i+1] == True) & (home_ft[i+2] == False) & (home_made[i-1] == False):
                    home_ft[i] = "2Shot"
                    i = i+2
                elif (home_ft[i+1] == True) & (home_ft[i+2] == True) & (home_made[i-1] == False):
                    home_ft[i] = "3shot"
                    i = i+3
                else:
                    home_ft[i] = "And1"
                    i = i+1
                    
            results_home = [home_ft.count("1Shot"), home_ft.count("2Shot"), home_ft.count("3shot"), 
                            home_ft.count("And1"), home_orb.count(True), home_tov.count(True), 
                            np.min(home_event), np.max(home_event), np.mean(home_event),
                            np.median(home_event), np.std(home_event)]
    
            #Add everything to final data frame
            
            #Getting times
            
            new_res = np.append(results, results_visit)
            results = np.append(new_res, results_home)
            results = np.append(results,day)
            results = np.append(results,month)
            results = np.append(results,year)
            
            
            over_res = pd.DataFrame(pd.Series(results))
            over_res.transpose().to_csv(box_file, mode = 'a', header = False,  index=False)
            
        except:
            next
        
        
        


#Example 
box_file = "Trip_dist.csv"

years = [2017, 2018]
months = [10,11, 12, 1,2,3,4]
days = range(1,32)




for year in years:
    for month in months:
        for day in days:
            print(day)
            print(month)
            print(year)
            try:
                scrapeTrips(day,month,year, box_file, first_run = False)
            except Exception:
                continue