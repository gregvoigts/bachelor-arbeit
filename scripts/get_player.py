import csv
from time import sleep
from typing import List
import requests
import json
from riotwatcher import LolWatcher, ApiError
import schemas
from pydantic import parse_file_as
from pydantic.json import pydantic_encoder

template_search_url = 'https://api.lolpros.gg/es/search?query={}&active=true'
league_template = '&league={}'

players_json = parse_file_as(List[schemas.Player],"players.json")

players = set(players_json)

# Extract all player tags for a specific League from the CSV
with open('2023_LoL_esports_match_data_from_OraclesElixir.csv',encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        if row['league'] == 'LEC' and row['playername'] != '':
            players.add(schemas.Player(name=row['playername']))

# Find the Summenors Names of this players with help of the lolpros site
for player in players:
    # If puuid is already present skip
    if player.puuid != None:
        continue
    search_query = (template_search_url+league_template).format(player.name,'LEC').replace(' ','+')
    res = requests.get(search_query)
    data = json.loads(res.content)
    # if no data found in the first place, remove the league restriction from query
    if len(data) == 0:
        search_query = template_search_url.format(player.name).replace(' ','+')
        res = requests.get(search_query)
        data = json.loads(res.content)
    for search_res in data:
        if search_res['name'].lower().replace(' ','') == player.name.lower().replace(' ',''):
            s_name = search_res['league_player']['accounts'][0]['summoner_name']
            player.summ_name = s_name
            sleep(0.01)
            break
    else:
        assert(True, "No account found")

# Init Riot API
lol_watcher = LolWatcher('RGAPI-650e5965-fd22-42fd-a2f6-fea3d5ab7a75')
my_region = 'euw1'

# Get puuid from riot api with summoner name
for player in players:
    # If puuid is already present skip
    if player.puuid != None or player.summ_name == None:
        continue
    profil = lol_watcher.summoner.by_name(my_region, player.summ_name)
    player.puuid=profil['puuid']

# Store back to file
with open('players.json', 'w') as file:
    player_list = [p.dict(exclude={"summ_name"}) for p in players]
    json.dump(player_list,file)

