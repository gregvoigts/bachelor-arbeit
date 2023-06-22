from auto_learn import auto_learn
from auto_regression import auto_regression
folders = ['all_games_simple_v2','lec_games_full','europe_games_full','all_games_matchups']


for folder in folders:
    try:
        auto_regression(folder)
    except Exception as e:
        print(f'error in folder {folder}')
        print(e)