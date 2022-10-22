from urllib.request import urlopen
from bs4 import BeautifulSoup

# url for the teams id
api_url = "https://dashboard.api-football.com/soccer/ids/teams/England"

# url to get PL team names 
standings_url = "https://www.espn.com/soccer/standings/_/league/eng.1"

# standings
standings_page = urlopen(standings_url)
standings_html = standings_page.read().decode("utf-8")
standings_soup = BeautifulSoup(html, "html.parser")

soup.findall("div", class_="team_link")


# api
api_page = urlopen(api_url)
api_html = api_page.read().decode("utf-8")
api_soup = BeautifulSoup(html, "html.parser")
