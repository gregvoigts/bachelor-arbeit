import csv
from datetime import datetime
from time import mktime
from typing import List
import numpy as np

from tinydb import TinyDB, Query
import schemas
from pydantic import parse_file_as


def get_winrate(winrates, patch: str, patches: List[schemas.Patch]) -> float:
    """
    Get the winrate of the champion in a specific patch.

    Parameters
    ----------
    winrates: dict
        Contains the winrate data.
    patch: str
        Patch for which we want the winrate.
    patches: List[schemas.Patch]
        List of patches.

    Returns
    -------
    float
        Winrate of the champion in the given patch.

    """
    lower = None
    upper = mktime(datetime.now().timetuple())*1000
    for p in patches:
        if lower != None:
            upper = p.date
            break
        if p.patch == patch:
            lower = p.date

    filtered_winrates = [
        winrate for winrate in winrates if lower <= winrate[0] < upper]

    if not filtered_winrates:
        return None  # No objects found within the specified range

    winrate = max(filtered_winrates, key=lambda obj: obj[0])
    return winrate[1]


def get_player_stats(player: schemas.PlayerWGames, champ: str) -> tuple:
    """
    Get the player stats.

    Parameters
    ----------
    player: schemas.PlayerWGames
        Player for which we want the stats.
    champ: str
        Champion for which we want the stats.

    Returns
    -------
    tuple
        Tuple containing the player stats.

    """
    total = 0
    gold = 0
    kills = 0
    damage = 0
    death = 0
    win = 0
    for game in player.games:
        game_length = (game.gameEndTimestamp - game.gameStartTimestamp) / 60000
        participant: schemas.Participant = list(
            filter(lambda p: p.puuid == player.puuid, game.participants))[0]
        if participant.championName == champ:
            total += 1
            gold += participant.goldEarned/game_length
            kills += participant.kills
            damage += participant.totalDamageDealtToChampions/game_length
            death += participant.deaths
            if participant.win:
                win += 1
    if total == 0:
        return 0, 0, 0, 0, 0
    return (win/total), (gold/total), (kills/total), (damage/total), (death/total)


games: List[schemas.LSTM_10Seq] = []

champ_db = TinyDB('champs.json')
ChampQ = Query()

player_db = TinyDB('pro_games.json')
PlayerQ = Query()

patches = parse_file_as(List[schemas.Patch], 'patches.json')

# Extract all player tags for a specific League from the CSV
with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    current_game: schemas.LSTM_10Seq = None
    for row in reader:
        if row['league'] == 'LEC' and row['playername'] != '':
            if current_game == None:
                current_game = schemas.LSTM_10Seq(gameId=row["gameid"],)
            if current_game.gameId != row["gameid"]:
                games.append(current_game)
                current_game = schemas.LSTM_10Seq(gameId=row["gameid"])
            champion_name = row['champion'].replace("'", "")
            # WTF RIOT PLS
            if champion_name == 'Wukong':
                champion_name = 'MonkeyKing'
            champ_winrates = champ_db.get(ChampQ.name == champion_name)
            player: schemas.PlayerWGames = schemas.PlayerWGames.parse_obj(
                player_db.get(PlayerQ.name == row["playername"]))

            winrate = get_winrate(
                champ_winrates['data'], row["patch"], patches)
            pro_winrate, goldAvg, killsAvg, damageAvg, deathAvg = get_player_stats(
                player, champion_name)
            player_data = schemas.LSTM_Player_Data(player_name=row["playername"],
                                                   champ_name=champion_name,
                                                   champ=champ_winrates.doc_id - 1,
                                                   champ_winrate=winrate,
                                                   pro_winrate=pro_winrate,
                                                   kills_avg=killsAvg,
                                                   gold_avg=goldAvg,
                                                   damage_avg=damageAvg,
                                                   deaths_avg=deathAvg
                                                   )

            if row['side'] == 'Blue':
                current_game.blue_win = row['result']
                current_game.__dict__[row['position'] + '_blue'] = player_data
            if row['side'] == 'Red':
                current_game.red_win = row['result']
                current_game.__dict__[row['position'] + '_red'] = player_data

x_arr = np.zeros((len(games),10,len(champ_db)+6),float)
y_arr = np.zeros((len(games),2),float)

for index,game in enumerate(games):
    x_arr[index],y_arr[index] = game.get_arrays(len(champ_db))

print(x_arr.shape)
print(y_arr.shape)

np.savez("game_data.npz", x=x_arr, y=y_arr)