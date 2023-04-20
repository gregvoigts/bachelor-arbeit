from datetime import datetime, timedelta
from time import mktime
from typing import List
from pydantic import parse_file_as
import schemas
from tinydb import TinyDB, Query
from riotwatcher import LolWatcher, ApiError

db = TinyDB('pro_games.json')
PlayerQ = Query()

# Load players
players_json = parse_file_as(List[schemas.Player],"players.json")

# Init Riot API
lol_watcher = LolWatcher('RGAPI-9bbd0af5-807c-4533-a1e3-e00f59d01a96')
my_region = 'euw1'

for player in players_json:
    res = db.search(PlayerQ.puuid == player.puuid)
    playerWGames: schemas.PlayerWGames
    if len(res) != 0:
        playerWGames = schemas.PlayerWGames.parse_obj(res[0])
    else:
        playerWGames = schemas.PlayerWGames(name=player.name, puuid=player.puuid)
        db.insert(playerWGames.dict())
    
    while True:
        # Find next game without information in Stored games
        for game in playerWGames.games:
            if game.win != None:
                continue
            # Get gameData from Riot
            game_details = lol_watcher.match.by_id(my_region,game.gameId)
            # Update model and DB
            partcipant = [x for x in game_details['info']['participants'] if x['puuid'] == playerWGames.puuid][0]
            game.championId = partcipant['championId']
            game.championName = partcipant['championName']
            game.gameStartTimestamp = game_details['info']['gameStartTimestamp']
            game.gameEndTimestamp = game_details['info']['gameEndTimestamp']
            game.goldEarned = partcipant['goldEarned']
            game.totalDamageDealtToChampions = partcipant['totalDamageDealtToChampions']
            game.win = partcipant['win']
            db.update({'games':playerWGames.dict()['games']},PlayerQ.puuid == playerWGames.puuid)

            # update latestGameTimestamp or earliestGameTimestamp if necessery
            if game.gameEndTimestamp > playerWGames.lastGameTimestamp:
                playerWGames.lastGameTimestamp = game.gameEndTimestamp
                db.update({'lastGameTimestamp':game.gameEndTimestamp},PlayerQ.puuid == playerWGames.puuid)

        print(f'All {len(playerWGames.games)} games from {playerWGames.name} where gathered')
        
        # if latest game in list was in the last 12 hours go to the next player
        if mktime((datetime.now() - timedelta(hours=12)).timetuple()) <= playerWGames.lastGameTimestamp/1000:
            print(f'Stop search for Games for {playerWGames.name}. Games up to date')
            break

        # Get next gameIds from Riot
        idList = lol_watcher.match.matchlist_by_puuid(my_region,playerWGames.puuid,start_time=playerWGames.getStartTime(),end_time=playerWGames.getEndTime(), count=100)

        # adapt prediction of days needed to play games
        if len(idList) >= 95:
            playerWGames.daysCount -= 5
            db.update({'daysCount':playerWGames.daysCount},PlayerQ.puuid == playerWGames.puuid)
        # if end time is in future, len isnt correkt
        elif len(idList) <= 55 and mktime(datetime.now().timetuple()) > playerWGames.getEndTime():
            playerWGames.daysCount += 5
            db.update({'daysCount':playerWGames.daysCount},PlayerQ.puuid == playerWGames.puuid)
        
        # If result is 100 games, cant be sure to dont miss games. 
        # So ignore result and try again next time with less days
        if len(idList) == 100:
            continue

        # If no more games found break loop
        if len(idList) == 0:
            print(f'Stop search for Games for {playerWGames.name}. No more games found')
            break

        for id in idList:
            playerWGames.games.append(schemas.Game(gameId=id))
        # Store ids to DB
        db.update({'games': playerWGames.dict()['games']},PlayerQ.puuid == playerWGames.puuid)
        print(f'Added {len(idList)} Games to {playerWGames.name}.')

    