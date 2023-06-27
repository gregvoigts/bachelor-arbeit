from auto_learn import auto_learn
from auto_regression import auto_regression
from auto_learn_autoencode import auto_learn_encoded
folders = ['lec_games_simple','europe_games_simple','lec_games_full','europe_games_full','all_games_simple_v2','all_games_matchups','all_games_champs_only','all_games_with_region','all_games_with_patch']


for folder in folders:
    try:
        auto_learn_encoded(folder)
    except Exception as e:
        print(f'error in folder {folder}')
        print(e)