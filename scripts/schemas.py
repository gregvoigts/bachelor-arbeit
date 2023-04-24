from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel, validator


start2023: int = 1672527600000

class BaseModel(PydanticBaseModel):
    class Config:
        orm_mode = True

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