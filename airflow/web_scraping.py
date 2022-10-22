import os
from urllib.request import urlopen
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()

# url to get PL team names 
standings_url = "https://www.espn.com/soccer/standings/_/league/eng.1"

# standings
standings_page = urlopen(standings_url)
standings_html = standings_page.read().decode("utf-8")
standings_soup = BeautifulSoup(standings_html, "html.parser")

results = standings_soup.find_all("div" , class_="team-link")

current_clubs = []

for result in results:
    club_links = result.find_all("a")
    club = club_links[2].text
    clubs.append(club)

print(clubs)

# api

# url for the teams id
api_url = "https://dashboard.api-football.com/soccer/ids/teams/England"

api_page = urlopen(api_url)
api_html = api_page.read().decode("utf-8")
api_soup = BeautifulSoup(api_html, "html.parser")

email = os.environ.get('EMAIL')
password = os.environ.get("PASSWORD")

print(email, password)