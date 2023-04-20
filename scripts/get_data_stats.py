from tinydb import TinyDB, Query

db = TinyDB('pro_games.json')

print(f'DB got data for {len(db)} players')

for player in db:
    print(f'{player["name"]} got {len(player["games"])} games')