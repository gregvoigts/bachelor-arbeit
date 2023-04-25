from tinydb import TinyDB, Query

db = TinyDB('pro_games.json')

print(f'DB got data for {len(db)} players')

games_total = 0

for player in db:
    games_total += len(player["games"])
    print(f'{player["name"]} got {len(player["games"])} games')
print(games_total)