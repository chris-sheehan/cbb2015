# College Hoops Player-Level Analysis

## S-R Scraping

## Get Team/Conference by Yearn
import numpy as np
import pandas as pd
import sqlite3
import logging
import time

from YearTeamsConferenceScraper import YearTeamsConferenceScraper
from TeamRosterScraper import TeamRosterScraper
from YearTeamGameSummary import YearTeamGameSummaryScraper
from GameBoxScraper import GameBoxScraper


logging.basicConfig(filename='box_scraping.log', level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)


_YEARS_TO_SCRAPE = range(2011, 2016)
_URL_BASE = "http://www.sports-reference.com"
DB_NAME = 'game_stats'
DB_NAME_ADV = 'game_stats_adv'

def connect_db():
	sqlite.connect('game_stats.db')

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
## dfTeams = pd.read_csv('teams.csv')
## dfTeams.year = dfTeams.year.map(int)
## dfTeams = dfTeams[dfTeams.year >= 2011]


def get_game_info_and_links(tm_link, year):
	global dfGamesFinal
	try:
		scraper = YearTeamGameSummaryScraper(year, tm_link)
		games = scraper.get_year_team_summaries()
		dfGames = pd.DataFrame(games)
		dfGamesFinal = pd.concat([dfGamesFinal, dfGames], axis = 0)
	except:
		pass

# dfGamesFinal = pd.DataFrame()
# dfTeams.apply(lambda r: get_game_info_and_links(r.tm_link, r.year), axis = 1)


def scrape_games_stat_tables(game_id):
	global dfGameStats
	global dfGameStatsAdvanced
	try:
		logger.info(game_id)
 		scraper = GameBoxScraper(game_id)
		dfStats, dfStatsAdvanced = scraper.get_game_stats()

		dfGameStats = pd.concat([dfGameStats, dfStats], axis = 0)
		dfGameStatsAdvanced = pd.concat([dfGameStatsAdvanced, dfStatsAdvanced], axis = 0)
	except:
		logger.info('Error Scraping: {gm}'.format(gm = game_id))
		pass

if __name__ == '__main__':
	dfGames = pd.read_csv('games_summary.csv')
	dfGames.sort('box', inplace = True)
	dfGames.reset_index(drop = True, inplace = True)

	dfGameStats = pd.DataFrame()
	dfGameStatsAdvanced = pd.DataFrame()
	# dfGames[['box']].drop_duplicates().head(10).apply(lambda g: scrape_games_stat_tables(g))

	conn = sqlite3.connect('game_stats.db')
	# Resume from #38667
	# for ii, g in enumerate(dfGames.box.unique()):
	for ii, g in enumerate(dfGames.ix[56215:].box.unique()):
		if (ii % 100 == 0) & (ii > 0):
			dfGameStats.to_sql('game_stats', conn, flavor = 'sqlite', if_exists = 'append')
			dfGameStatsAdvanced.to_sql('game_stats_adv', conn, flavor = 'sqlite', if_exists = 'append')
			dfGameStats = pd.DataFrame()
			dfGameStatsAdvanced = pd.DataFrame()
			print g
		scrape_games_stat_tables(g)
		time.sleep(.5)
	# dfGameStats.to_csv('games_stats.csv', index = False)
	# dfGameStatsAdvanced.to_csv('games_stats_adv.csv', index = False)
	if dfGameStats.empty == False:
		dfGameStats.to_sql('game_stats', conn, flavor = 'sqlite', if_exists = 'append')
		dfGameStatsAdvanced.to_sql('game_stats_adv', conn, flavor = 'sqlite', if_exists = 'append')
	conn.close()
