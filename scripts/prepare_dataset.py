import csv
from datetime import datetime
from time import mktime
from typing import List, Optional
import numpy as np

from tinydb import TinyDB, Query
import schemas
from pydantic import parse_file_as

from datasetprep_util import get_player_stats, get_winrate

folder = 'europe_games_full'

leagues = ['LEC','EM','PRM','TCL','EBL','ESLOL','GLL','HM','LFL','LFL2','LPLOL','NLC','PGN','SL','UL']

games: List[schemas.Array_Complet] = []

players = parse_file_as(List[schemas.Player],"players.json")

champ_db = TinyDB('champs.json')
ChampQ = Query()

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
PlayerQ = Query()

patches = parse_file_as(List[schemas.Patch], 'patches.json')

# Extract all player tags for a specific League from the CSV
with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    current_game: Optional[schemas.Array_Complet] = None
    for row in reader:
        if row['league'] in leagues and row['playername'] != '':
            if current_game == None:
                current_game = schemas.Array_Complet(gameId=row["gameid"],)
            if current_game.gameId != row["gameid"]:
                if current_game.complete():
                    games.append(current_game)
                    print(f"Added {current_game.gameId}")
                else:
                    print(f"Game {current_game.gameId} incomplete")
                current_game = schemas.Array_Complet(gameId=row["gameid"])
            champion_name = row['champion'].replace("'", "").replace(" ","")
            # WTF RIOT PLS
            if champion_name == 'Wukong':
                champion_name = 'MonkeyKing'
            if champion_name == 'RenataGlasc':
                champion_name = 'Renata'
            champ_winrates = champ_db.get(ChampQ.name.map(str.lower) == champion_name.lower())
            player_index = players.index(schemas.Player(name=row['playername'])) # type: ignore
            league = players[player_index].league
            if league == None:
                print(f'No league for player {row["playername"]}')
                continue
            player_raw = dbs[league].get(PlayerQ.name == row["playername"])
            if player_raw == None:
                print(f'No data found for player {row["playername"]} in league {row["league"]}')
                continue
            player: schemas.PlayerWGames = schemas.PlayerWGames.parse_obj(player_raw)
            if champ_winrates == None:
                print(f"No champ_winrates Found for {champion_name}")
                continue

            winrate = get_winrate(
                champ_winrates['data'], row["patch"], patches)
            pro_winrate, goldAvg, killsAvg, damageAvg, deathAvg = get_player_stats(
                player, champion_name)
            player_data = schemas.Array_Player_Data(player_name=row["playername"],
                                                   champ_name=champion_name,
                                                   champ=champ_winrates.doc_id - 1,
                                                   champ_winrate=winrate,
                                                   pro_winrate=pro_winrate,
                                                   kills_avg=killsAvg,
                                                   gold_avg=goldAvg,
                                                   damage_avg=damageAvg,
                                                   deaths_avg=deathAvg
                                                   )

            if row['side'] == 'Blue':
                current_game.blue_win = int(row['result'])
                current_game.__dict__[row['position'] + '_blue'] = player_data
            if row['side'] == 'Red':
                current_game.red_win = int(row['result'])
                current_game.__dict__[row['position'] + '_red'] = player_data

x_arr = np.zeros((len(games),len(champ_db)+(6*10)),float)
y_arr = np.zeros((len(games),2),float)

for index,game in enumerate(games):
    x_arr[index],y_arr[index] = game.get_arrays(len(champ_db))

print(x_arr.shape)
print(y_arr.shape)

np.savez(f"{folder}/game_data.npz", x=x_arr, y=y_arr)