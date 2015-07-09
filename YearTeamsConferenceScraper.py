# import numpy a np
# import pandas as pd

import requests
from bs4 import BeautifulSoup as bsoup

_URL_PATTERN_SEASON_RATINGS = "http://www.sports-reference.com/cbb/seasons/{year}-ratings.html"

class YearTeamsConferenceScraper(object):
	def __init__(self, year):
		self.year = year

	def get_season_soup(self):
		url_season = _URL_PATTERN_SEASON_RATINGS.format(year = self.year)
		html = requests.get(url_season)
		soup = bsoup(html.text, 'html.parser')
		self.soup = soup

	def get_teams(self):
		teams = []
		tbl_body = self.soup.find('table',{'id':'ratings'}).find('tbody')
		rows = tbl_body.findAll('tr')
		for row in rows:
			row_class = row.attrs['class'][0]
			if row_class == '':
				cells = row.findAll('td', {'align' : 'left'})
				tm, conf = [c.text for c in cells]
				tm_link = cells[0].find('a').attrs['href'].split('/')[3]
				teams.append({'year' : self.year, 'team' : tm, 'tm_link' : tm_link, 'conference' : conf})
		self.teams = teams