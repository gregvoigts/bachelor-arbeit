# Script to load player champion data from league of graphs

from time import sleep
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent


url = "https://www.leagueofgraphs.com/de/champions/stats/{}"

url_search ="https://www.trackingthepros.com/search?s={}"
headers = {'User-Agent':UserAgent().chrome}

def get_proside(player_name:str):
    response = requests.get(url_search.format(player_name), headers=headers)

    sleep(0.5)

    if response.status_code == 200:  # successful response
        soup = BeautifulSoup(response.content, "html.parser")
        found_profiles = soup.find_all("a", {"class": "label-primary"})
        if len(found_profiles) != 0:
            for profil in found_profiles:
                if profil.contents[0] == player_name:
                    return profil.link
        else:
            print("Could not find the profiles div element")
    else:
        print("Request failed with status code", response.status_code)

def get_account_names(player_name, profil_link):
    response = requests.get(profil_link,headers=headers)
    sleep(0.5)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content,"html.parser")
        box_body = soup.find("div",{"class":"box-body"})
        accounts = box_body.contents[4]

get_proside("Caps")