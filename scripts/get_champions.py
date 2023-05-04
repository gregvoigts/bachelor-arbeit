from time import sleep
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import re
import json
from riotwatcher import LolWatcher
from tinydb import TinyDB, Query

lol_watcher = LolWatcher('RGAPI-a536f78e-70e0-48ac-ba9f-a47842f6227f')
my_region = 'euw1'

db = TinyDB('champs.json')
Champions = Query()

# First we get the latest version of the game from data dragon
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']

# Lets get some champions
current_champ_list = lol_watcher.data_dragon.champions(champions_version)

url = "https://www.leagueofgraphs.com/de/champions/stats/{}"
headers = {'User-Agent':UserAgent().chrome}

for champ in current_champ_list['data'].keys():
    response = requests.get(url.format(champ.lower()),headers=headers)
    sleep(0.5)
    if response.status_code == 200:  # successful response
        soup = BeautifulSoup(response.content, "html.parser")
        winratehistorie_div = soup.find("div", {"class": "winrateHistoryBox"})
        if winratehistorie_div is not None:
            script_content = winratehistorie_div.contents[3].contents[0]
            data = re.search(r'\[(\[.*?\],?)*\]',script_content).group()
            data_arr = json.loads(data)
            db.upsert({'name':champ, 'data':data_arr},Champions.name == champ)
            print(f'Update data for {champ}')
        else:
            print("Could not find the winratehistorie div element")
    else:
        print("Request failed with status code", response.status_code)