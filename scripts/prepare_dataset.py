import csv
from datetime import datetime
from time import mktime
from typing import List, Optional
import numpy as np

from tinydb import TinyDB, Query
import schemas
from pydantic import parse_file_as

from datasetprep_util import get_player_stats, get_winrate




games: List[schemas.Array_Complet] = []

champ_db = TinyDB('champs.json')
ChampQ = Query()

player_db = TinyDB('pro_games.json')
PlayerQ = Query()

patches = parse_file_as(List[schemas.Patch], 'patches.json')

# Extract all player tags for a specific League from the CSV
with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    current_game: Optional[schemas.Array_Complet] = None
    for row in reader:
        if row['league'] == 'LEC' and row['playername'] != '':
            if current_game == None:
                current_game = schemas.Array_Complet(gameId=row["gameid"],)
            if current_game.gameId != row["gameid"]:
                games.append(current_game)
                print(f"Added {current_game.gameId}")
                current_game = schemas.Array_Complet(gameId=row["gameid"])
            champion_name = row['champion'].replace("'", "").replace(" ","")
            # WTF RIOT PLS
            if champion_name == 'Wukong':
                champion_name = 'MonkeyKing'
            if champion_name == 'RenataGlasc':
                champion_name = 'Renata'
            champ_winrates = champ_db.get(ChampQ.name.map(str.lower) == champion_name.lower())
            player: schemas.PlayerWGames = schemas.PlayerWGames.parse_obj(
                player_db.get(PlayerQ.name == row["playername"]))
            if champ_winrates == None:
                print(f"No champ_winrates Found for {champion_name}")
                exit(1)

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

np.savez("game_data.npz", x=x_arr, y=y_arr)