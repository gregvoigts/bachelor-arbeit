import csv
from typing import List, Optional, Dict
import numpy as np
from pydantic import parse_file_as, validator
from tinydb import TinyDB,Query
from datetime import datetime as dt
import schemas
from datasetprep_util import get_winrate

# divides two numbers
# when division by zero return zero
def costum_divide(a:float,b:float):
    if b == 0:
        return 0
    return round(a/b,2)

class ChampDataSingle(schemas.BaseModel):
    result:int
    gamelength:int
    kills:int
    deaths:int
    assists:int
    damagetochampions:int
    visionscore:int
    totalgold:int

    def gold_per_minute(self):
        return self.totalgold/self.gamelength * 1.0

    def vision_pre_minute(self):
        return self.visionscore/self.gamelength * 1.0
    
    def dmg_per_minute(self):
        return self.damagetochampions/self.gamelength * 1.0

    def get_kda(self):
        if self.deaths == 0:
            return self.kills + self.assists
        return (self.kills + self.assists)/self.deaths
    
    @validator('visionscore','damagetochampions','totalgold',pre=True, always=True)
    def check_value(cls,v):
        if v == '' or v == None:
            return 0
        return v

class ChampData(schemas.BaseModel):
    name:str
    id:int
    games_count:float = 0.0
    wins:int = 0
    kda:float = 0.0
    gold_per_minute:float = 0.0
    dmg_pre_minute:float = 0.0
    vision_per_minute:float = 0.0

    def addSingle(self,single:ChampDataSingle):
        self.games_count += 1
        self.wins += single.result
        self.kda += single.get_kda()
        self.gold_per_minute += single.gold_per_minute()
        self.dmg_pre_minute += single.dmg_per_minute()
        self.vision_per_minute += single.vision_pre_minute()

    def exportData(self):
        x = np.zeros(0,dtype=float)
        x = np.append(x,self.id)
        x = np.append(x,self.games_count)
        x = np.append(x,costum_divide(self.wins, self.games_count))
        x = np.append(x,costum_divide(self.kda ,self.games_count))
        x = np.append(x,costum_divide(self.gold_per_minute , self.games_count))
        x = np.append(x,costum_divide(self.dmg_pre_minute ,self.games_count))
        x = np.append(x,costum_divide(self.vision_per_minute , self.games_count))
        return x

    def exportDataSmall(self):
        x = np.zeros(0,dtype=float)
        x = np.append(x,self.id)
        x = np.append(x,self.games_count)
        x = np.append(x,costum_divide(self.wins, self.games_count))
        x = np.append(x,costum_divide(self.kda ,self.games_count))
        return x


class PlayerData(schemas.BaseModel):
    champs:Dict[str,ChampData] = {}

class Game(schemas.BaseModel):
    gameId:str
    league:str
    patch:float
    league_code:int
    win:int

    top_blue: List[float] = []
    jng_blue: List[float] = []
    mid_blue: List[float] = []
    bot_blue: List[float] = []
    sup_blue: List[float] = []

    top_red: List[float] = []
    jng_red: List[float] = []
    mid_red: List[float] = []
    bot_red: List[float] = []
    sup_red: List[float] = []

    def complete(self) -> bool:
        """
        Check if all fields are not None.
        Returns:
            bool: True if all fields are not None, False otherwise.
        """
        fields = [
            self.top_blue,
            self.jng_blue,
            self.mid_blue,
            self.bot_blue,
            self.sup_blue,
            self.top_red,
            self.jng_red,
            self.mid_red,
            self.bot_red,
            self.sup_red,
        ]

        return all(len(field) == 8 for field in fields)

    # create array with league, patch and fields for every position
    def get_arrays(self,champ_count,league_counts):
        x = np.zeros(0, dtype=float)
        # add regions
        # reg = np.zeros(league_counts, dtype=float)
        # reg[self.league_code] = 1
        # x = np.append(x,reg)
        # # add patch
        # x = np.append(x,self.patch)
        # add winrates
        x = np.append(x, (
            self.top_blue, 
            self.jng_blue, 
            self.mid_blue, 
            self.bot_blue, 
            self.sup_blue, 
            self.top_red, 
            self.jng_red, 
            self.mid_red, 
            self.bot_red, 
            self.sup_red))

        return x, self.win

    # create array with league, patch and fields for every position
    def get_arrays_small(self,champ_count,league_counts):
        x = np.zeros(0, dtype=float)
        # add winrates
        x = np.append(x, (
            self.top_blue, 
            self.jng_blue, 
            self.mid_blue, 
            self.bot_blue, 
            self.sup_blue, 
            self.top_red, 
            self.jng_red, 
            self.mid_red, 
            self.bot_red, 
            self.sup_red))

        return x, self.win
#folder_small = 'classifier/from_costaetal_self_small'

folder = 'classifier/europe_games_pro_only'

all_leagues = []

# all european leagues
leagues = ['LEC','EM','PRM','TCL','EBL','ESLOL','GLL','HM','LFL','LFL2','LPLOL','NLC','PGN','SL','UL']

# init champion DB with all champions and winrates per date
champ_db = TinyDB('champs.json')
ChampQ = Query()

# list with pathches and dates
patches = parse_file_as(List[schemas.Patch], 'patches.json')

players:Dict[str,PlayerData] = {}

games: List[Game] = []

games_small: List[Game] = []

with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    current_game: Optional[Game] = None
    current_game_small: Optional[Game] = None
    #endtime = dt.strptime('2021-03-24 00:00:00','%Y-%m-%d %H:%M:%S')
    # iterate over all rows and filter for leagues and skip team rows
    for row in reader:
        if row['position'] != 'team' and row["datacompleteness"] == "complete" and row['league'] in leagues:
            # create new game
            if current_game == None or current_game.gameId != row["gameid"]:
                # store game
                if current_game != None and current_game_small != None:
                    if current_game.complete():
                        games.append(current_game)
                        games_small.append(current_game_small)
                        print(f"Added {current_game.gameId}")
                    else:
                        print(f"Game {current_game.gameId} incomplete")
                # t = dt.strptime(row['date'],'%Y-%m-%d %H:%M:%S')
                # if t >= endtime:
                #     break
                patch = float(row['patch'])
                try:
                    all_leagues.index(row['league'])
                except ValueError:
                    all_leagues.append(row['league'])
                current_game = Game(gameId=row["gameid"],win=int(row['result']),
                                                   patch=round((patch-13)*10,1), 
                                                   league=row['league'],
                                                    league_code=all_leagues.index(row['league']))#type:ignore
                current_game_small = Game(gameId=row["gameid"],win=int(row['result']),
                                                   patch=round((patch-13)*10,1), 
                                                   league=row['league'],
                                                    league_code=all_leagues.index(row['league']))#type:ignore

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
            winrate:float = get_winrate(
                champ_winrates['data'], row["patch"], patches) # type: ignore
            
            # add player data
            if row['playername'] not in players.keys():
                players[row['playername']] = PlayerData()
            if row['champion'] not in players[row['playername']].champs.keys():
                players[row['playername']].champs[row['champion']] = ChampData(name=row['champion'],id=champ_winrates.doc_id-1)
            player_array = players[row['playername']].champs[row['champion']].exportData()
            #player_array_small = players[row['playername']].champs[row['champion']].exportDataSmall()
            player_array = np.append(player_array,winrate)
            if row['side'] == 'Blue':
                current_game.__dict__[row['position'] + '_blue'] = player_array
            if row['side'] == 'Red':
                current_game.__dict__[row['position'] + '_red'] = player_array
            
            # if row['side'] == 'Blue':
            #     current_game_small.__dict__[row['position'] + '_blue'] = player_array_small
            # if row['side'] == 'Red':
            #     current_game_small.__dict__[row['position'] + '_red'] = player_array_small
            
            # add game to player statistic
            single = ChampDataSingle.parse_obj(row)
            players[row['playername']].champs[row['champion']].addSingle(single)

# init numpy arrays
x,y = games[0].get_arrays(len(champ_db),len(all_leagues))
x_arr = np.zeros((len(games),len(x)),float)
y_arr = np.zeros((len(games)),float)

# init small numpy arrays
# x,y = games_small[0].get_arrays_small(len(champ_db),len(all_leagues))
# x_arr_small = np.zeros((len(games),len(x)),float)
# y_arr_small = np.zeros((len(games)),float)

# fill numpy array from games
for index,game in enumerate(games):
    x_arr[index],y_arr[index] = game.get_arrays(len(champ_db),len(all_leagues))
# for index,game in enumerate(games_small):
#     x_arr_small[index],y_arr_small[index] = game.get_arrays_small(len(champ_db),len(all_leagues))

# Search for duplicated rows and adapt winner
# for i in range(len(x_arr)):
#     if y_arr[i] != 1 and y_arr[i] != 0:
#         continue
#     duplications = []
#     for j in range(i+1,len(x_arr)):        
#         if np.array_equal(x_arr[i],x_arr[j]):
#             duplications.append(j)
#     sum = y_arr[i]
#     for row in duplications:
#         sum += y_arr[row]
#     sum = sum / (len(duplications)+1)
#     y_arr[i] = sum
#     for row in duplications:
#         y_arr[row] = sum
    

print(x_arr.shape)
print(y_arr.shape)

# print(x_arr_small.shape)
# print(y_arr_small.shape)

# save to file
np.savez(f"{folder}/game_data.npz", x=x_arr, y=y_arr)
# np.savez(f"{folder_small}/game_data.npz", x=x_arr_small, y=y_arr_small)