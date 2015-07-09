# College Hoops Player-Level Analysis

## S-R Scraping

## Get Team/Conference by Yearn
import numpy as np
import pandas as pd
import logging

# import requests
# from bs4 import BeautifulSoup as bsoup
from YearTeamsConferenceScraper import YearTeamsConferenceScraper
from TeamRosterScraper import TeamRosterScraper


logging.basicConfig(filename='roster_scraping.log', level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)


_YEARS_TO_SCRAPE = range(2001, 2016)
_URL_BASE = "http://www.sports-reference.com"

def get_all_teams_and_conferences():
	df = pd.DataFrame(None, columns = ['conference', 'team', 'tm_link', 'year'])
	for year in _YEARS_TO_SCRAPE:
		print year
		years_teams_scraper = YearTeamsConferenceScraper(year)
		df_yr = get_season_teams_conferences(years_teams_scraper)
		df = pd.concat([df, df_yr], axis = 0)
	return df

def get_season_teams_conferences(scraper):
	scraper.get_season_soup()
	scraper.get_teams()
	cols = scraper.teams[0].keys()
	return pd.DataFrame(scraper.teams, columns = cols)



def get_team_roster(tm, tm_link, yr):
	print yr, tm
	scraper = TeamRosterScraper(tm, tm_link, yr)
	scraper.get_roster_soup()
	scraper.get_roster_flds()
	scraper.get_roster()
	cols = ['Class', 'Ht', 'Player', 'Pos', 'Team', 'player_link', 'Year']
	df = pd.DataFrame(scraper.players, columns = cols)
	return df

def concat_all_teams_rosters(lst_dfRosters):
	df = pd.DataFrame(None, columns = ['Class', 'Ht', 'Player', 'Pos', 'Team', 'player_link', 'Year'])


# dfTeams = get_all_teams_and_conferences()
# dfTeams.reset_index(inplace = True)
# dfTeams.to_csv('teams.csv', index = False)
dfTeams = pd.read_csv('teams.csv')
dfTeams.year = dfTeams.year.map(int)
# lst_dfRosters = dfTeams.head().apply(lambda r: get_team_roster(r.team, r.tm_link, int(r.year)), axis = 1)
lst_dfRosters = []
for n in dfTeams.index[528:]:
	r = dfTeams.loc[n]
	try:
		lst_dfRosters.append(get_team_roster(r.team, r.tm_link, r.year))
	except Exception, e:
		print 'Error scraping: {tm_link}, {year}'.format(tm_link = r.tm_link, year = r.year)
		logger.info('Error scraping: {tm_link}, {year}'.format(tm_link = r.tm_link, year = r.year))
