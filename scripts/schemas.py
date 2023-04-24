from typing import Optional
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

class Game(BaseModel):
    gameId: str
    win: Optional[bool]
    totalDamageDealtToChampions: Optional[int]
    goldEarned: Optional[int]
    championId: Optional[int]
    championName: Optional[str]
    gameStartTimestamp: Optional[int]
    gameEndTimestamp: Optional[int]
    # add champs for each team
    # add red or blue side
    # redTeam: Optionla[List[Champs]]
    # blueTeam: Optionla[List[Champs]]

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
        latest = max(values['games'], key=lambda data: data.gameEndTimestamp, default=v).gameEndTimestamp
        print(f'{v}:{latest}')
        if v != latest:
            print(f'Unmatching timestamps for {values["name"]}')
        return latest