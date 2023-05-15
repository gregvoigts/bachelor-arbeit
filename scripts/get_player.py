import csv
from time import sleep
from typing import List
import requests
import json
from riotwatcher import LolWatcher, ApiError
import schemas
from pydantic import parse_file_as
from pydantic.json import pydantic_encoder
from unidecode import unidecode

template_search_url = 'https://api.lolpros.gg/es/search?query={}&active=true'
league_template = '&league={}'

leagues = ['LEC','EM','PRM','TCL','EBL','ESLOL','GLL','HM','LFL','LFL2','LPLOL','NLC','PGN','SL','UL']

players_json = parse_file_as(List[schemas.Player],"players.json")

players = set(players_json)

# Extract all player tags for a specific League from the CSV
with open('2023_LoL_esports_match_data_from_OraclesElixir.csv',encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        if row['league'] in leagues and row['playername'] != '':
            players.add(schemas.Player(name=row['playername'],puuid=None,summ_name=None, league = row['league']))

# Find the Summenors Names of this players with help of the lolpros site
for player in players:
    # If puuid is already present skip
    if player.puuid != None:
        continue
    search_query = (template_search_url+league_template).format(player.name,player.league).replace(' ','+')
    res = requests.get(search_query)
    data = json.loads(res.content)
    # if no data found in the first place, remove the league restriction from query
    if len(data) == 0:
        search_query = template_search_url.format(player.name).replace(' ','+')
        res = requests.get(search_query)
        data = json.loads(res.content)
    for search_res in data:
        if unidecode(search_res['name'].lower().replace(' ','')) == unidecode(player.name.lower().replace(' ','')):
            s_name = search_res['league_player']['accounts'][0]['summoner_name']
            player.summ_name = s_name
            sleep(0.01)
            print(f'Account found for {player.name}')
            break
    else:
        print(f'No account found for {player.name}')

# Init Riot API
lol_watcher = LolWatcher('RGAPI-a3f3cc52-6511-44d0-9290-f30105cc560f')
my_region = 'euw1'

# Get puuid from riot api with summoner name
for player in players:
    # If puuid is already present skip
    if player.puuid != None or player.summ_name == None:
        continue
    try:
        profil = lol_watcher.summoner.by_name(my_region, player.summ_name)
        player.puuid=profil['puuid']  # type: ignore
    except:
        print(f'Api error for {player.summ_name}')
# Store back to file
with open('players.json', 'w') as file:
    player_list = [p.dict(exclude={"summ_name"}) for p in players]
    json.dump(player_list,file)

