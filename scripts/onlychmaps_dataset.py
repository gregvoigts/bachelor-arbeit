import csv
from typing import List, Optional
import numpy as np
from pydantic import parse_file_as
from tinydb import TinyDB,Query

import schemas
from datasetprep_util import get_winrate


folder = 'all_games_simple_v2'

# init champion DB with all champions and winrates per date
champ_db = TinyDB('champs.json')
ChampQ = Query()

# all european leagues
leagues = ['LEC','EM','PRM','TCL','EBL','ESLOL','GLL','HM','LFL','LFL2','LPLOL','NLC','PGN','SL','UL']

# list with pathches and dates
patches = parse_file_as(List[schemas.Patch], 'patches.json')

games: List[schemas.Game_simple] = []


with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    current_game: Optional[schemas.Game_simple] = None
    # iterate over all rows and filter for leagues and skip team rows
    for row in reader:
        if row['position'] != 'team' and row["datacompleteness"] == "complete": #row['league'] in leagues and
            # create new game
            if current_game == None:
                current_game = schemas.Game_simple(gameId=row["gameid"],)#type:ignore
            # store game and create new if new gameId
            if current_game.gameId != row["gameid"]:
                assert len(current_game.blue) == 5 and len(current_game.red) == 5, f"champ count isnt 5 for {current_game.gameId}"
                games.append(current_game)
                print(f"Added {current_game.gameId}")
                current_game = schemas.Game_simple(gameId=row["gameid"])#type:ignore

            # create championname
            champion_name = row['champion'].replace("'", "").replace(" ","").replace(".","")
            # WTF RIOT PLS
            if champion_name == 'Wukong':
                champion_name = 'MonkeyKing'
            if champion_name == 'RenataGlasc':
                champion_name = 'Renata'
            if champion_name == 'Nunu&Willump':
                champion_name = 'Nunu'
            
            # get winrate for champ on current patch
            champ_winrates = champ_db.get(ChampQ.name.map(str.lower) == champion_name.lower())

            assert champ_winrates != None ,f'no winrates for {champion_name}' 

            if row['patch'] == None or row["patch"] == "":
                print(current_game.gameId)     
            winrate = get_winrate(
                champ_winrates['data'], row["patch"], patches)
            
            # write champ_data to game object
            if row['side'] == 'Blue':
                current_game.blue.append(champ_winrates.doc_id-1)
                current_game.blue_win = int(row['result'])
                current_game.__dict__[row['position'] + '_blue'] = winrate
            if row['side'] == 'Red':
                current_game.red.append(champ_winrates.doc_id-1)
                current_game.red_win = int(row['result'])
                current_game.__dict__[row['position'] + '_red'] = winrate

# init numpy arrays
x_arr = np.zeros((len(games),len(champ_db)+(10)),float)
y_arr = np.zeros((len(games)),float)

# fill numpy array from games
for index,game in enumerate(games):
    x_arr[index],y_arr[index] = game.get_arrays(len(champ_db))

# Search for duplicated rows and adapt winner
for i in range(len(x_arr)):
    if y_arr[i] != 1 and y_arr[i] != 0:
        continue
    duplications = []
    for j in range(i+1,len(x_arr)):        
        if np.array_equal(x_arr[i],x_arr[j]):
            duplications.append(j)
    sum = y_arr[i]
    for row in duplications:
        sum += y_arr[row]
    sum = sum / (len(duplications)+1)
    y_arr[i] = sum
    for row in duplications:
        y_arr[row] = sum
    

print(x_arr.shape)
print(y_arr.shape)

# save to file
np.savez(f"{folder}/game_data.npz", x=x_arr, y=y_arr)