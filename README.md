# basketball_code

`2015Teams.csv` - File containing team names in the style of sports-reference. Must be in same directory as ScrapePlayers.py for the script to work. Teams are taken from all D1 basketball schools in 2015 but can be modified to include former schools.

`BoxScoreScrape.py` - Function for scraping college basketball scores from sports-reference.com. Start and end dates are input and .csv file is outputted with complete box scores.

`ScrapePlayers.py` - Pulls yearly stats from sports-reference.com for college basketball players. Start and end year is input and a .csv file is output. 

`dailyScrape.py` - Like `BoxScoreScrape.py` but designed to be used daily in the task manager

`dailyOddsNCAA.py` - Code used to pull NCAA basketball odds each day from https://www.sportsbookreview.com. Inputs are day, month, year, output file location and whether it is the first run. First run takes a True or False logical argument and must be set to True on the initial run if one wants to populate the column names then turned off for subsequent runs. Each run appends the day's odds to the end of the odds file. The output is Teams, Dates, Spread, Moneyline and the Over for the day.
