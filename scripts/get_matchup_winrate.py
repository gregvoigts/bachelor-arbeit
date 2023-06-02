from time import sleep
from typing import List
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import re
import json
from riotwatcher import LolWatcher
from tinydb import TinyDB, Query

def getchamps(div) -> List:
    table = div.contents[3]
    rows = table.findAll('tr')
    champs = []
    for row in rows:
        if len(row.find_all("th")) > 0 or 'see_more_hidden_button_row' in row.attrs['class'] :
                continue
        winrate = row.find("progressbar").attrs["data-value"]
        champ = row.find("span").text
        champs.append({"name":champ,"winrate":winrate})
    return champs


lol_watcher = LolWatcher('RGAPI-f688c749-487d-48e7-bc50-b4bbb6b81d44')
my_region = 'euw1'

db = TinyDB('matchups.json')
Champions = Query()

# First we get the latest version of the game from data dragon
versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']

# Lets get some champions
current_champ_list = lol_watcher.data_dragon.champions(champions_version)

url = "https://www.leagueofgraphs.com/de/champions/counters/{}"
headers = {'User-Agent':UserAgent().chrome}

for champ in current_champ_list['data'].keys():
    response = requests.get(url.format(champ.lower()),headers=headers)
    sleep(0.5)
    if response.status_code == 200:  # successful response
        soup = BeautifulSoup(response.content, "html.parser")
        winning_div = soup.select('.row > .columns > .boxContainer > .box')[3]
        losing_div = soup.select('.row > .columns > .boxContainer > .box')[4]
        
        matchups = getchamps(winning_div)
        matchups += getchamps(losing_div)
        db.upsert({'name':champ,'matchups':matchups},Champions.name == champ)
    else:
        print("Request failed with status code", response.status_code)