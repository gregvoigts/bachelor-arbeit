from datetime import datetime
from time import mktime
from typing import List
import schemas


def get_winrate(winrates, patch: str, patches: List[schemas.Patch]):
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

    assert lower != None, f"no lower found {patch}"

    filtered_winrates = []
    for winrate in winrates:
        if winrate == None:
            print(winrates)
            continue
        if lower <= winrate[0] < upper:
            filtered_winrates.append(winrate)

    if not filtered_winrates:
        return None  # No objects found within the specified range

    winrate = max(filtered_winrates, key=lambda obj: obj[0])
    return winrate[1]

def get_matchup_winrate(winrates,opponend):
    for champ in winrates['matchups']:
        if champ['name'].lower() == opponend.lower():
            return champ['winrate']
    return 0.5

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
        if game.gameEndTimestamp == None or game.gameStartTimestamp == None or game.participants == None:
            continue
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
