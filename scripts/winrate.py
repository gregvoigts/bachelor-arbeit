from typing import List
from pydantic import parse_file_as
from tinydb import TinyDB, Query
import schemas

# Load players
players_json = parse_file_as(List[schemas.Player],"players.json")

db = TinyDB('pro_games.json')
PlayerQ = Query()

print('Programm to get winrate for a specific player on a specific champion')
for i, player in enumerate(players_json):
    print(f'[{i}] {player.name}')

index = int(input('Typ  index of player: '))

champion = input('For wich Champion?: ')

player:schemas.PlayerWGames = schemas.PlayerWGames.parse_obj(db.get(PlayerQ.puuid == players_json[index].puuid))

total = 0
win = 0
for game in player.games:
    participant:schemas.Participant = list(filter(lambda p: p.puuid == player.puuid,game.participants))[0]
    if participant.championName == champion:
        total += 1
        if participant.win:
            win += 1

print(f'{player.name} has a winrate of {win/total*100}% on Champion {champion} in {total} games.')
