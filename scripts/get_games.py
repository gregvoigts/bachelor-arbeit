from datetime import datetime, timedelta
from time import mktime
from typing import List
from pydantic import parse_file_as
import schemas
from tinydb import TinyDB, Query
from riotwatcher import LolWatcher, ApiError

PlayerQ = Query()

dbs = {'LEC':TinyDB('pro_games_LEC.json'),
       'EM':TinyDB('pro_games_EM.json'),
       'PRM':TinyDB('pro_games_PRM.json'),
       'TCL':TinyDB('pro_games_TCL.json'),
       'EBL':TinyDB('pro_games_EBL.json'),
       'ESLOL':TinyDB('pro_games_ESLOL.json'),
       'GLL':TinyDB('pro_games_GLL.json'),
       'HM':TinyDB('pro_games_HM.json'),
       'LFL':TinyDB('pro_games_LFL.json'),
       'LFL2':TinyDB('pro_games_LFL2.json'),
       'LPLOL':TinyDB('pro_games_LPLOL.json'),
       'NLC':TinyDB('pro_games_NLC.json'),
       'PGN':TinyDB('pro_games_PGN.json'),
       'SL':TinyDB('pro_games_SL.json'),
       'UL':TinyDB('pro_games_UL.json')}

# Load players
players_json = parse_file_as(List[schemas.Player],"players.json")

# Init Riot API
lol_watcher = LolWatcher('RGAPI-8de519e2-6856-4812-9e74-1ada5a85b7ee')
my_region = 'euw1'

for player in players_json:
    if player.puuid == None:
        continue
    if player.league == None:
        print(f'Missing league for {player.name}')
        continue
    res = dbs[player.league].search(PlayerQ.puuid == player.puuid)
    playerWGames: schemas.PlayerWGames
    if len(res) != 0:
        playerWGames = schemas.PlayerWGames.parse_obj(res[0])
    else:
        playerWGames = schemas.PlayerWGames(name=player.name, puuid=player.puuid, summ_name=None, league=player.league)
        dbs[player.league].insert(playerWGames.dict())
    
    while True:
        # Find next game without information in Stored games
        for index,game in enumerate(playerWGames.games):
            if game.gameVersion != None:
                continue
            # Get gameData from Riot
            game_details = lol_watcher.match.by_id(my_region,game.matchId)
            # Update model and DB
            game_details['info']['matchId'] = game.matchId # type: ignore
            playerWGames.games[index] = schemas.Game.parse_obj(game_details['info']) # type: ignore
            '''partcipant = [x for x in game_details['info']['participants'] if x['puuid'] == playerWGames.puuid][0]
            game.championId = partcipant['championId']
            game.championName = partcipant['championName']
            game.gameStartTimestamp = game_details['info']['gameStartTimestamp']
            game.gameEndTimestamp = game_details['info']['gameEndTimestamp']
            game.goldEarned = partcipant['goldEarned']
            game.totalDamageDealtToChampions = partcipant['totalDamageDealtToChampions']
            game.win = partcipant['win']'''
            dbs[player.league].update({'games':playerWGames.dict()['games']},PlayerQ.puuid == playerWGames.puuid)

            # update latestGameTimestamp if necessery
            if playerWGames.games[index].gameEndTimestamp > playerWGames.lastGameTimestamp: # type: ignore
                playerWGames.lastGameTimestamp = playerWGames.games[index].gameEndTimestamp # type: ignore
                dbs[player.league].update({'lastGameTimestamp':playerWGames.games[index].gameEndTimestamp},PlayerQ.puuid == playerWGames.puuid)

        print(f'All {len(playerWGames.games)} games from {playerWGames.name} where gathered')
        
        # if latest game in list was in the last 12 hours go to the next player
        if mktime((datetime.now() - timedelta(hours=12)).timetuple()) <= playerWGames.lastGameTimestamp/1000: # type: ignore
            print(f'Stop search for Games for {playerWGames.name}. Games up to date')
            break

        # Get next gameIds from Riot
        idList = lol_watcher.match.matchlist_by_puuid(my_region,playerWGames.puuid,start_time=playerWGames.getStartTime(),end_time=playerWGames.getEndTime(), count=100,type='ranked') # type: ignore

        # adapt prediction of days needed to play games
        if len(idList) >= 95: # type: ignore
            playerWGames.daysCount -= 5
            dbs[player.league].update({'daysCount':playerWGames.daysCount},PlayerQ.puuid == playerWGames.puuid)
        # if end time is in future, len isnt correkt
        elif len(idList) <= 55 and mktime(datetime.now().timetuple()) > playerWGames.getEndTime():# type: ignore
            playerWGames.daysCount += 5
            dbs[player.league].update({'daysCount':playerWGames.daysCount},PlayerQ.puuid == playerWGames.puuid)
        
        # If result is 100 games, cant be sure to dont miss games. 
        # So ignore result and try again next time with less days
        if len(idList) == 100:# type: ignore
            continue

        # If no games set current time or end time as new Start time
        if len(idList) == 0:# type: ignore
            playerWGames.lastGameTimestamp = min(mktime(datetime.now().timetuple())*1000,playerWGames.getEndTime()*1000)# type: ignore
            dbs[player.league].update({'lastGameTimestamp':playerWGames.lastGameTimestamp},PlayerQ.puuid == playerWGames.puuid)
            continue

        for id in idList:
            playerWGames.games.append(schemas.Game(matchId=id))# type: ignore
        # Store ids to DB
        dbs[player.league].update({'games': playerWGames.dict()['games']},PlayerQ.puuid == playerWGames.puuid)
        print(f'Added {len(idList)} Games to {playerWGames.name}.')# type: ignore

    