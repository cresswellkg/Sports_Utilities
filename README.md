# basketball_code

`2015Teams.csv` - File containing team names in the style of sports-reference. Must be in same directory as ScrapePlayers.py for the script to work. Teams are taken from all D1 basketball schools in 2015 but can be modified to include former schools.

`BoxScoreScrape.py` - Function for scraping college basketball scores from sports-reference.com. Start and end dates are input and .csv file is outputted with complete box scores.

`ScrapePlayers.py` - Pulls yearly stats from sports-reference.com for college basketball players. Start and end year is input and a .csv file is output. 

`dailyScrape.py` - Like `BoxScoreScrape.py` but designed to be used daily in the task manager

`dailyOddsNCAA.py` - Code used to pull NCAA basketball odds each day from https://www.sportsbookreview.com. Inputs are day, month, year, output file location and whether it is the first run. First run takes a True or False logical argument and must be set to True on the initial run if one wants to populate the column names then turned off for subsequent runs. Each run appends the day's odds to the end of the odds file. The output is Teams, Dates, Spread, Moneyline and the Over for the day.

`scrapeTrips.py` - Uses the play-by-play feature of sports-reference to calculate the number of each type of foul (1-shot, 2-shot, 3-short or And1). The results allow you to accurately calculate the number of trips down the court. (Only available for 2017-2018 season).

# Suggestions

dailyScrape is much more streamline at the moment. For quickest results first run daily scrape with the first_run option equal to True (This must be done on a day that actually had games played). Then create a list of months, days and years of interest then loop over those. The same process should be followed for dailyOddsNCAA if you want historical odds.
