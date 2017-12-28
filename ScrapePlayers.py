from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import csv
import requests
import os
import re

#Use American to get column names

def scrapePlayers(start_year, end_year):
    page = requests.get('http://www.sports-reference.com/cbb/schools/american/2017.html')
    soup = BeautifulSoup(page.content, 'html.parser')
    html = list(soup.children)[2]
    pergame = soup.select_one("#per_game")
    columnName = [item['data-stat'] for item in pergame.find_all(attrs={'data-stat' : True})]
    columnName = pd.unique(columnName)
    
    #Read in csv of teams and extract schools
    
    schools = pd.read_csv('2015Teams.csv', sep=',',header=None)
    schools = schools[0].str.lower()
    schools = np.array(schools)
    schools = [re.sub(" ", "-",x) for x in schools]
    schools = [re.sub("\(", "",x) for x in schools]
    schools = [re.sub("\)", "",x) for x in schools]
    schools = [re.sub("university-of-", "",x) for x in schools]
    schools = [re.sub("&", "",x) for x in schools]
    schools = [re.sub("uc-", "california-",x) for x in schools]
    schools = [re.sub("\\.", "",x) for x in schools]
    schools = [re.sub("\\'", "",x) for x in schools]
    schools = [re.sub("siu-", "southern-illinois-",x) for x in schools]
    schools = [re.sub("texas-rio-grande-valley", "texas-pan-american",x) for x in schools]
    schools = [re.sub("vmi", "virginia-military-institute",x) for x in schools]
    schools = [re.sub("--", "-",x) for x in schools]
    
    yearres = pd.DataFrame()
    for k in range(start_year,end_year):
        overresults = pd.DataFrame()
        for i in range(0, len(schools)):
            try:
                page = requests.get('http://www.sports-reference.com/cbb/schools/'+str(schools[i])+'/'+str(k)+'.html')
            except Exception:
                continue
            soup = BeautifulSoup(page.content, 'html.parser')
            html = list(soup.children)[2]
            pergame = soup.select_one("#per_game") 
            results = pd.DataFrame()
            for j in range(0, len(columnName)):
                stat = []
                index = 0
                try:
                    all = pergame.find_all('td',attrs={'data-stat' : str(columnName[j])})
                except Exception:
                    continue
                for z in range(0, len(all)-1):
                    stat.append(all[z].text.strip())
                results[str(columnName[j])] = stat
            results["Team"] = np.repeat(schools[i],len(results))
            results["Year"] = np.repeat(k, len(results))
            overresults = pd.concat([overresults,results])
        yearres = pd.concat([yearres, overresults])

    
    
    
    
    
    
    
