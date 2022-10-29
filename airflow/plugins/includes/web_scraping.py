import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

load_dotenv()

email = os.environ.get("EMAIL")
password = os.environ.get("PASSWORD")

def get_current_teams(url):
    """
    description: Scrape the current premier league teams from the url passed in
    params:
        url (str): link to the standings
    """
    # standings
    standings_page = urlopen(url)
    standings_html = standings_page.read().decode("utf-8")
    standings_soup = BeautifulSoup(standings_html, "html.parser")

    results = standings_soup.find_all("div", class_="team-link")

    current_clubs = []

    for result in results:
        club_links = result.find_all("a")
        club = club_links[2].text
        current_clubs.append(club)
    return current_clubs


def get_english_teams(login_url, target_url, email, password):
    """
    params:
        login_url(str): url for logging in the api-football
        target_url(str): target url for extracting neccessary data after logging in
        email(str): login email
        password(str): login passsword
    """
    cwd = os.getcwd()
    chromedriver_path = cwd + '/drivers/chromedriver'

    driver = webdriver.Chrome(chromedriver_path)  # launch the webdriver
    driver.get(login_url)  # login page

    try:
        driver.find_element_by_name("email").send_keys(email)  # enter email
        driver.find_element_by_name("pass").send_keys(password)  # enter password
        driver.find_element_by_tag_name(
            "button"
        ).click()  # submit the email and password

        # wait the ready state to be complete
        WebDriverWait(driver=driver, timeout=10).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )

        error_message = "Wrong Email or Password."  # error message returned from the login page for wrong credentials

        errors = driver.find_elements_by_id("swal2-content")  # get the errors (if any)

        for e in errors:
            print(e.text)

        # print status of the login
        if any(error_message in e.text for e in errors):
            print("[!] Login failed")
        else:
            print("[+] Login successful")

        driver.get(target_url)  # load the page for getting the team name and id

        select = Select(driver.find_element_by_name("dataTable_length"))
        select.select_by_value("50")

        content = driver.page_source
        soup = BeautifulSoup(content, features="lxml")

        table = soup.find("table", id="dataTable")
        t_body = table.find("tbody")

        id_to_team_name = {}

        for i, body in enumerate(t_body):
            if i > 0:
                values = body.find_all("td")
                extracted_values = [value.text for value in values]
                id_to_team_name[extracted_values[1].strip()] = extracted_values[0]

        return id_to_team_name

    except:
        print("an error occured")
    finally:
        driver.close()


def generate_csv(current_clubs, id_to_team_mapping, file_name):
    id_team_name_keys = id_team_name_mapping.keys()

    needed_mappings = {}

    for i, club in enumerate(current_clubs):
        if club == "Wolverhampton Wanderers":
            current_clubs[i] = "Wolves"
            club = "Wolves"
        elif club == "West Ham United":
            current_clubs[i] = "West Ham"
            club = "West Ham"

        parts = club.split(" ")
        if club in id_team_name_keys:
            needed_mappings[club] = id_team_name_mapping[club]
        elif parts[0] in id_team_name_keys:
            needed_mappings[club] = id_team_name_mapping[parts[0]]
        elif parts[1] in id_team_name_keys:
            needed_mappings[club] = id_team_name_mapping[parts[1]]

    team_names = needed_mappings.keys()
    team_ids = needed_mappings.values()

    data = {"team_id": team_ids, "team_name": team_names}

    df = pd.DataFrame(columns=["team_id", "team_name"], data=data)

    # save the csv file
    df.to_parquet(file_name, index=False)
