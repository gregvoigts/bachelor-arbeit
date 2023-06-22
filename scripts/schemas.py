from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel, validator
import numpy as np


start2023: int = 1672527600000


class BaseModel(PydanticBaseModel):
    class Config:
        orm_mode = True


class Patch(BaseModel):
    patch: str
    date: int
    code: float


class Player(BaseModel):
    name: str
    puuid: Optional[str]
    summ_name: Optional[str]
    league: Optional[str]

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
    teamPosition: str
    puuid: str
    totalDamageDealtToChampions: int
    win: bool
    teamId: int


class Game(BaseModel):
    matchId: str
    gameStartTimestamp: Optional[int]
    gameEndTimestamp: Optional[int]
    gameVersion: Optional[str]
    participants: Optional[List[Participant]]


class PlayerWGames(Player):
    games: List[Game] = []
    lastGameTimestamp: int = start2023
    # how many days this player needs to play between 50 and 99 games
    # used in for gathering games from riot
    daysCount: int = 21

    def getEndTime(self):
        return int(self.lastGameTimestamp/1000 + (self.daysCount*24*60*60))

    def getStartTime(self):
        return int(self.lastGameTimestamp/1000+120)

    @validator('lastGameTimestamp')
    def must_be_highest_timestamp(cls, v, values):
        latest = v
        if not 'games' in values:
            return v
        for game in values['games']:
            if game.gameEndTimestamp != None and game.gameEndTimestamp > latest:
                latest = game.gameEndTimestamp
        if v != latest:
            print(f'Unmatching timestamps for {values["name"]}')
        return latest

class PlayerstatsForChamp(BaseModel):
    champ_name:str
    games:int
    winrate:float
    kda:float
    gold:float

class PlayerWStats(Player):
    champs:List[PlayerstatsForChamp] = []

class Array_Player_Data(BaseModel):
    player_name: str = ""
    champ_name: str = ""
    champ: int = 0
    champ_winrate: Optional[float]
    pro_winrate: Optional[float]
    gold_avg: Optional[float]
    kills_avg: Optional[float]
    damage_avg: Optional[float]
    deaths_avg: Optional[float]

    # normalizes Stats so the better player gets 1 and the oponend
    # gets his procentage of the better players stat
    def normalize_stats(self, oponend):
        if self.gold_avg != None and oponend.gold_avg != None:
            max_gold = max(self.gold_avg, oponend.gold_avg)
            if max_gold > 0:
                self.gold_avg = self.gold_avg/max_gold

        if self.kills_avg != None and oponend.kills_avg != None:
            max_kills = max(self.kills_avg, oponend.kills_avg)
            if max_kills > 0:
                self.kills_avg = self.kills_avg/max_kills

        if self.damage_avg != None and oponend.damage_avg != None:
            max_damage = max(self.damage_avg, oponend.damage_avg)
            if max_damage > 0:
                self.damage_avg = self.damage_avg/max_damage

        if self.deaths_avg != None and oponend.deaths_avg != None:
            max_deaths = max(self.deaths_avg, oponend.deaths_avg)
            if max_deaths > 0:
                self.deaths_avg = self.deaths_avg/max_deaths

        return self

    # Build an numpy array with one Hot for the Champion and all the stats
    def get_array(self):
        arr = np.zeros(6, dtype=float)
        arr[0] = self.champ_winrate
        arr[1] = self.pro_winrate
        arr[2] = self.gold_avg
        arr[3] = self.kills_avg
        arr[4] = self.damage_avg
        arr[5] = self.deaths_avg
        return arr


class Array_Complet(BaseModel):
    gameId: str = ""

    top_blue: Array_Player_Data = None # type: ignore
    jng_blue: Array_Player_Data = None# type: ignore
    mid_blue: Array_Player_Data = None# type: ignore
    bot_blue: Array_Player_Data = None# type: ignore
    sup_blue: Array_Player_Data = None# type: ignore

    top_red: Array_Player_Data = None# type: ignore
    jng_red: Array_Player_Data = None# type: ignore
    mid_red: Array_Player_Data = None# type: ignore
    bot_red: Array_Player_Data = None# type: ignore
    sup_red: Array_Player_Data = None# type: ignore

    red_win: int = 0
    blue_win: int = 0
    
    def complete(self) -> bool:
        """
        Check if all fields are not None.
        Returns:
            bool: True if all fields are not None, False otherwise.
        """
        fields = [
            self.gameId,
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

        return all(field is not None for field in fields)

    def get_arrays(self, champ_count):
        x = np.zeros(champ_count, dtype=float)
        # fill champs
        for player in [self.top_blue, self.jng_blue, self.mid_blue, self.bot_blue, self.sup_blue]:
            x[player.champ] = 1
        for player in [self.top_red, self.jng_red, self.mid_red, self.bot_red, self.sup_red]:
            x[player.champ] = -1
        # add player info
        x = np.append(x, (
            self.top_blue.normalize_stats(self.top_red).get_array(), 
            self.jng_blue.normalize_stats(self.jng_red).get_array(), 
            self.mid_blue.normalize_stats(self.mid_red).get_array(), 
            self.bot_blue.normalize_stats(self.bot_red).get_array(), 
            self.sup_blue.normalize_stats(self.sup_red).get_array(), 
            self.top_red.normalize_stats(self.top_blue).get_array(), 
            self.jng_red.normalize_stats(self.jng_blue).get_array(), 
            self.mid_red.normalize_stats(self.mid_blue).get_array(), 
            self.bot_red.normalize_stats(self.bot_blue).get_array(), 
            self.sup_red.normalize_stats(self.sup_blue).get_array()))

        y = np.array([self.blue_win, self.red_win])

        return x, y

class Game_simple(BaseModel):
    gameId: str = ""

    patch: float = 0

    region: int = -1

    red: List[int] = []
    blue: List[int] = []

    top_blue: int = 0
    jng_blue: int = 0
    mid_blue: int = 0
    bot_blue: int = 0
    sup_blue: int = 0

    top_red: int = 0
    jng_red: int = 0
    mid_red: int = 0
    bot_red: int = 0
    sup_red: int = 0

    red_win: int = 0
    blue_win: int = 0

    def get_arrays(self,champ_count,league_counts):
        x = np.zeros(champ_count, dtype=float)
        # fill champs
        for champ in self.blue:
            x[champ] = 1
        for champ in self.red:
            x[champ] = -1
        # add regions
        # reg = np.zeros(league_counts, dtype=float)
        # reg[self.region] = 1
        # x = np.append(x,reg)
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

        y = 0

        if self.blue_win == 1:
            y = 1

        return x, y

class Game_matchup(BaseModel):
    gameId: str = ""

    red: List[int] = []
    blue: List[int] = []

    top_blue: str = ""
    jng_blue: str = ""
    mid_blue: str = ""
    bot_blue: str = ""
    sup_blue: str = ""

    top_red: str = ""
    jng_red: str = ""
    mid_red: str = ""
    bot_red: str = ""
    sup_red: str = ""

    top: float = 0
    jng: float = 0
    mid: float = 0
    bot: float = 0
    sup: float = 0

    red_win: int = 0
    blue_win: int = 0

    def get_arrays(self,champ_count):
        x = np.zeros(champ_count, dtype=float)
        # fill champs
        for champ in self.blue:
            x[champ] = 1
        for champ in self.red:
            x[champ] = -1
        # add winrates
        x = np.append(x, (
            self.top,
            self.jng,
            self.mid,
            self.bot,
            self.sup))

        y = 0

        if self.blue_win == 1:
            y = 1

        return x, y