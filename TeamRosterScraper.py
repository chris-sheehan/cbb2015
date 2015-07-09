import numpy as np
# import pandas as pd

import requests
from bs4 import BeautifulSoup as bsoup

_URL_PATTERN_TEAM_ROSTER = "http://www.sports-reference.com/cbb/schools/{tm_link}/{year}.html"

class TeamRosterScraper(object):
	def __init__(self, tm, tm_link, year):
		self.tm = tm
		self.tm_link = tm_link
		self.year = year

	def get_roster_soup(self):
		self.url = _URL_PATTERN_TEAM_ROSTER.format(tm_link = self.tm_link, year = self.year)
		html = requests.get(self.url)
		soup = bsoup(html.text, 'html.parser')
		self.soup = soup


	def get_roster_flds(self):
		roster = self.soup.find('table',{'id':'roster'})
		flds = ['Team'] + [th.text for th in roster.find('thead').find('tr').findAll('th')][:-1] + ['Year']
		self.roster_flds = flds

	def get_roster(self):
		roster = self.soup.find('table',{'id':'roster'})
		players = []
		rows = roster.tbody.findAll('tr')
		for row in rows:
			cells = row.findAll('td')
			player = [self.tm_link] + [td.text for td in cells][:4] + [self.year]
			player[4] = self.calc_inches(player[4]) if player[4] != '' else np.nan
			player_dict = {fld : val for fld, val in zip(self.roster_flds, player)}
			
			player_dict['player_link'] = cells[0].find('a').attrs['href'].split('/')[3].replace('.html', '')
			players.append(player_dict)

		self.players = players

	def calc_inches(self, str_height):
		height = int(str_height.split('-')[0]) * 12 + int(str_height.split('-')[1])
		return height

	def get_players(self):
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