from datetime import datetime
from typing import List
from pydantic import parse_file_as
from tinydb import TinyDB, Query

import schemas

# Load players
players_json = parse_file_as(List[schemas.Player],"players.json")

count_players = {'LEC':0,
       'EM':0,
       'PRM':0,
       'TCL':0,
       'EBL':0,
       'ESLOL':0,
       'GLL':0,
       'HM':0,
       'LFL':0,
       'LFL2':0,
       'LPLOL':0,
       'NLC':0,
       'PGN':0,
       'SL':0,
       'UL':0}

total = 0

for player in players_json:
    total += 1
    count_players[player.league] += 1

print(count_players)
print(total)

dbs = {'LEC':TinyDB('pro_games_LEC.json'),
       'EM':TinyDB('pro_games_EM.json'),
       'PRM':TinyDB('pro_games_PRM.json'),
       'TCL':TinyDB('pro_games_TCL.json'),
       'EBL':TinyDB('pro_games_EBL.json'),
       'ESLOL':TinyDB('pro_games_ESLOL.json'),
       'GLL':TinyDB('pro_games_GLL.json'),
       'HM':TinyDB('pro_games_HM.json'),
       'LFL':TinyDB('pro_games_LFL.json'),
       'LFL2':TinyDB('pro_games_LFL2.json'),
       'LPLOL':TinyDB('pro_games_LPLOL.json'),
       'NLC':TinyDB('pro_games_NLC.json'),
       'PGN':TinyDB('pro_games_PGN.json'),
       'SL':TinyDB('pro_games_SL.json'),
       'UL':TinyDB('pro_games_UL.json')}

total_got = 0

for key,db in dbs.items():
     total_got += len(db)
     print(f'DB {key} got data for {len(db)} players of {count_players[key]}')

print(total_got)
# games_total = 0

# for player in dbs['LEC']:
#     p = schemas.PlayerWGames.parse_obj(player)
#     print(datetime.fromtimestamp(p.lastGameTimestamp/1000.0))
#     games_total += len(player["games"])
#     print(f'{player["name"]} got {len(player["games"])} games')
# print(games_total)

# 520 of 775