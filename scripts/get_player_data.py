# Script to load player champion data from league of graphs

import csv
from time import sleep
from typing import List
from bs4 import BeautifulSoup
from pydantic import parse_file_as
import requests
from fake_useragent import UserAgent

import schemas



url_search ="https://www.trackingthepros.com/search?s={}"
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}

def get_proside(player_name:str):
    response = requests.get(url_search.format(player_name), headers=headers)

    sleep(0.5)

    if response.status_code == 200:  # successful response
        soup = BeautifulSoup(response.content, "html.parser")
        found_profiles = soup.find_all("a", {"class": "label-primary"})
        if len(found_profiles) != 0:
            for profil in found_profiles:
                if profil.contents[0] == player_name:
                    return profil.attrs["href"]
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
        accounts = box_body.contents[9] # type: ignore
        active_accounts = accounts.find_all_next("tr",{"class":None,"id":None})
        account_list = []
        for account in active_accounts:
            name = account.contents[0].contents[1]
            region = account.contents[0].contents[0].contents[0].replace("[","").replace("]","")
            account_list.append((region,name))
        return account_list
    else:
        print("Request failed with status code", response.status_code)

def get_champ_data(region:str,name:str):
    response = requests.get(url.format(region.lower(),name.replace(" ","+")),headers=headers)

    sleep(0.5)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content,"html.parser")
        table_div = soup.find("div",{"data-tab-id":"championsData-soloqueue"})
        table_rows = table_div.find_all("tr")
        stats:List[schemas.PlayerstatsForChamp] = []
        for row in table_rows:
            if len(row.find_all("th")) > 0:
                continue
            # get name
            champ_name = row.contents[1].find("span",{"class":"name"}).contents[0]
            # get games count
            games = row.contents[3].find("progressbar").attrs["data-value"]
            # get winrate
            winrate = row.contents[5].find("progressbar",).attrs["data-value"]
            # get kda
            kda = row.contents[7].attrs["data-sort-value"]
            # get gold
            gold = row.contents[11].contents[1].contents[0]
            stats.append(schemas.PlayerstatsForChamp(champ_name=champ_name,games=games,winrate=winrate,kda=kda,gold=gold))
        return stats
    return None

leagues = ['LEC','EM','PRM','TCL','EBL','ESLOL','GLL','HM','LFL','LFL2','LPLOL','NLC','PGN','SL','UL']

players_json = parse_file_as(List[schemas.Player],"players.json")

players = set(players_json)

# Extract all player tags for a specific League from the CSV
with open('2023_LoL_esports_match_data_from_OraclesElixir.csv',encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        if row['league'] in leagues and row['playername'] != '':
            players.add(schemas.PlayerWStats(name=row['playername'],puuid=None,summ_name=None, league = row['league']))

print(f'Found {len(players)} Players')

for player in players:
    link = get_proside(player.name)
    if link == None:
        print(f'Skip {player.name} no profil link found')
        continue
    list = get_account_names(player.name,link)
    if list == None or len(list) == 0:
        print(f'Skip {player.name} no accounts found')
        continue
    stats = get_champ_data(list[0][0],list[0][1])
    player.champs = stats
