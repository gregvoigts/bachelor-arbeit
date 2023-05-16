import csv
from typing import List, Optional
import numpy as np
from pydantic import parse_file_as
from tinydb import TinyDB,Query

import schemas
from datasetprep_util import get_winrate

champ_db = TinyDB('champs.json')
ChampQ = Query()

games: List[schemas.Game_simple] = []
leagues = ['LEC','EM','PRM','TCL','EBL','ESLOL','GLL','HM','LFL','LFL2','LPLOL','NLC','PGN','SL','UL']
patches = parse_file_as(List[schemas.Patch], 'patches.json')

with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    current_game: Optional[schemas.Game_simple] = None
    for row in reader:
        if row['league'] in leagues and row['playername'] != '':
            if current_game == None:
                current_game = schemas.Game_simple(gameId=row["gameid"],)#type:ignore
            if current_game.gameId != row["gameid"]:
                games.append(current_game)
                print(f"Added {current_game.gameId}")
                current_game = schemas.Game_simple(gameId=row["gameid"])#type:ignore
            champion_name = row['champion'].replace("'", "").replace(" ","").replace(".","")
            # WTF RIOT PLS
            if champion_name == 'Wukong':
                champion_name = 'MonkeyKing'
            if champion_name == 'RenataGlasc':
                champion_name = 'Renata'
            if champion_name == 'Nunu&Willump':
                champion_name = 'Nunu'
            champ_winrates = champ_db.get(ChampQ.name.map(str.lower) == champion_name.lower())
            if champ_winrates == None:
                assert champ_winrates != None ,f'no winrates for {champion_name}'
                
            winrate = get_winrate(
                champ_winrates['data'], row["patch"], patches)
            
            if row['side'] == 'Blue':
                current_game.blue.append(champ_winrates.doc_id-1)
                current_game.blue_win = int(row['result'])
                current_game.__dict__[row['position'] + '_blue'] = winrate
            if row['side'] == 'Red':
                current_game.red.append(champ_winrates.doc_id-1)
                current_game.red_win = int(row['result'])
                current_game.__dict__[row['position'] + '_red'] = winrate

x_arr = np.zeros((len(games),len(champ_db)+(10)),float)
y_arr = np.zeros((len(games),2),float)

for index,game in enumerate(games):
    x_arr[index],y_arr[index] = game.get_arrays(len(champ_db))

print(x_arr.shape)
print(y_arr.shape)

np.savez("game_data_champs_only.npz", x=x_arr, y=y_arr)