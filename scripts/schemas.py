from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel, validator
import numpy as np


start2023: int = 1672527600000

class BaseModel(PydanticBaseModel):
    class Config:
        orm_mode = True

class Patch(BaseModel):
    patch:str
    date:int
class Player(BaseModel):
    name: str
    puuid: Optional[str]
    summ_name : Optional[str]

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class Participant(BaseModel):
    deaths: int
    championId: int
    championName: str
    goldEarned: int
    kills: int
    teamPosition:str
    puuid:str
    totalDamageDealtToChampions: int
    win:bool
    teamId:int
class Game(BaseModel):
    matchId: str
    gameStartTimestamp: Optional[int]
    gameEndTimestamp: Optional[int]
    gameVersion: Optional[str]
    participants: Optional[List[Participant]]


class PlayerWGames(Player):
    games: list[Game] = []
    lastGameTimestamp: int = start2023
    # how many days this player needs to play between 50 and 99 games
    # used in for gathering games from riot
    daysCount: int = 21

    def getEndTime(self):
        return int(self.lastGameTimestamp/1000 + (self.daysCount*24*60*60))
    
    def getStartTime(self):
        return int(self.lastGameTimestamp/1000+120)
    
    @validator('lastGameTimestamp')
    def must_be_highest_timestamp(cls,v,values):
        latest = v
        if not 'games' in values:
            return v
        for game in values['games']:
            if game.gameEndTimestamp != None and game.gameEndTimestamp > latest:
                latest = game.gameEndTimestamp
        print(f'{v}:{latest}')
        if v != latest:
            print(f'Unmatching timestamps for {values["name"]}')
        return latest

class LSTM_Player_Data(BaseModel):
    player_name:str = ""
    champ_name:str = ""
    champ:int = 0
    champ_winrate:float = 0
    pro_winrate:float = 0
    gold_avg:float = 0
    kills_avg:float = 0
    damage_avg:float = 0
    deaths_avg:float = 0

    # normalizes Stats so the better player gets 1 and the oponend
    # gets his procentage of the better players stat
    def normalize_stats(self, oponend):
        max_gold = max(self.gold_avg,oponend.gold_avg)
        if max_gold > 0:
            self.gold_avg = self.gold_avg/max_gold

        max_kills = max(self.kills_avg,oponend.kills_avg)
        if max_kills > 0:
            self.kills_avg = self.kills_avg/max_kills

        max_damage = max(self.damage_avg,oponend.damage_avg)
        if max_damage > 0:
            self.damage_avg = self.damage_avg/max_damage

        max_deaths = max(self.deaths_avg,oponend.deaths_avg)
        if max_deaths > 0:
            self.deaths_avg = self.deaths_avg/max_deaths

        return self

    # Build an numpy array with one Hot for the Champion and all the stats
    def get_array(self, champ_count):
        arr = np.zeros(champ_count+6, dtype=float)
        arr[self.champ] = 1
        arr[champ_count] = self.champ_winrate
        arr[champ_count+1] = self.pro_winrate
        arr[champ_count+2] = self.gold_avg
        arr[champ_count+3] = self.kills_avg
        arr[champ_count+4] = self.damage_avg
        arr[champ_count+5] = self.deaths_avg
        return arr
    
class LSTM_Match_Up(BaseModel):
    red:LSTM_Player_Data
    blue:LSTM_Player_Data

class LSTM_5Seq(BaseModel):
    gameId:str

    top:LSTM_Match_Up
    jng:LSTM_Match_Up
    mid:LSTM_Match_Up
    bot:LSTM_Match_Up
    sup:LSTM_Match_Up

    red_win:int
    blue_win:int

class LSTM_10Seq(BaseModel):
    gameId:str = ""

    top_blue:LSTM_Player_Data = LSTM_Player_Data()
    jng_blue:LSTM_Player_Data= LSTM_Player_Data()
    mid_blue:LSTM_Player_Data= LSTM_Player_Data()
    bot_blue:LSTM_Player_Data= LSTM_Player_Data()
    sup_blue:LSTM_Player_Data= LSTM_Player_Data()

    top_red:LSTM_Player_Data= LSTM_Player_Data()
    jng_red:LSTM_Player_Data= LSTM_Player_Data()
    mid_red:LSTM_Player_Data= LSTM_Player_Data()
    bot_red:LSTM_Player_Data= LSTM_Player_Data()
    sup_red:LSTM_Player_Data= LSTM_Player_Data()

    red_win:int = 0
    blue_win:int = 0
    
    def get_arrays(self, champ_count):
        x = np.zeros((10,champ_count+6), dtype=float)
        x[0] = self.top_blue.normalize_stats(self.top_red).get_array(champ_count)
        x[1] = self.jng_blue.normalize_stats(self.jng_red).get_array(champ_count)
        x[2] = self.mid_blue.normalize_stats(self.mid_red).get_array(champ_count)
        x[3] = self.bot_blue.normalize_stats(self.bot_red).get_array(champ_count)
        x[4] = self.sup_blue.normalize_stats(self.sup_red).get_array(champ_count)
        
        x[5] = self.top_red.normalize_stats(self.top_blue).get_array(champ_count)
        x[6] = self.jng_red.normalize_stats(self.jng_blue).get_array(champ_count)
        x[7] = self.mid_red.normalize_stats(self.mid_blue).get_array(champ_count)
        x[8] = self.bot_red.normalize_stats(self.bot_blue).get_array(champ_count)
        x[9] = self.sup_red.normalize_stats(self.sup_blue).get_array(champ_count)

        y = np.array([self.blue_win,self.red_win])

        return x,y
