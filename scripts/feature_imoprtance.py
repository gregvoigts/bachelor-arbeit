from sklearn.inspection import permutation_importance
import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from tinydb import Query, TinyDB
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

root ='classifier'

files = {
    #'lec_games_simple':['randsplit','autoencode'],
    #'europe_games_full':['randsplit','autoencode'],
    #'all_games_pro_only':['randsplit'],
    'all_games_simple_v2':['randsplit','autoencode']}

def calc_feature(folder,method):
    with np.load(f'{root}/{folder}/game_data.npz') as f:
        data_x = f['x']
        data_y = f['y']
    
    names = []

    if method == 'autoencode':
        # load the model from file
        encoder = load_model('encoder.h5')

        # run PCA to reduce sparse champion matrix
        only_champs,other = np.array_split(data_x,[163],axis=1)
        reduced = encoder.predict(only_champs)
        data_x = np.concatenate((reduced,other),axis=1)

        names.extend(autoencode)  
    elif folder == 'all_games_pro_only_small':
        names = feature_names_pro
    else:
        names.extend(champs_names)
    
    if folder == 'europe_games_full':
        names.extend(feature_names_full)
    elif folder != 'all_games_pro_only_small':
        names.extend(feature_names_simple)

    # x_train, x_test = np.split(data_x,[int(.9 * len(data_x))])
    # y_train, y_test = np.split(data_y,[int(.9 * len(data_y))])
    x_train,x_test,y_train,y_test = train_test_split(data_x,data_y,test_size=0.2, random_state=42)

    with open(f'{root}/{folder}/classifier_{method}.pkl','rb') as f:
        classi = pickle.load(f)

    result = permutation_importance(
        classi, x_test, y_test, n_repeats=10, random_state=42, n_jobs=2
    )


    importances = pd.Series(result.importances_mean, index=names) # type: ignore

    importances.to_csv(f'{root}/{folder}/importance_{method}.csv',sep=';', decimal=',')

    # plt.figure(num=None,figsize=(100,100),dpi=80,facecolor='w',edgecolor='k')
    # fig, ax = plt.subplots()
    # importances.plot.bar(yerr=result.importances_std, ax=ax) # type: ignore
    # ax.set_title("Feature importances using permutation on full model")
    # ax.set_ylabel("Mean accuracy decrease")
    # fig.tight_layout()
    # plt.show()

# init champion DB with all champions and winrates per date
champ_db = TinyDB('champs.json')
ChampQ = Query()

champ_db.all()

champs_names = [doc['name'] for doc in champ_db.all()]

autoencode = [f'encode_{i}' for i in enumerate(range(82))]

feature_names_simple = []

feature_names_full = []

feature_names_pro = []

stats = ['champwr','prowr','gold','kills','dmg','deaths']

pro_stats = ['champId','games_count','wins','kda']

pos = ['top_blue','jng_blue','mid_blue','bot_blue','sup_blue','top_red','jng_red','mid_red','bot_red','sup_red']

for p in pos:
    for s in stats:
        feature_names_full.append(f'{p}_{s}')

for p in pos:
    feature_names_simple.append(f'{p}_champwr')

for p in pos:
    for s in pro_stats:
        feature_names_pro.append(f'{p}_{s}')

for key, value in files.items():
    for file in value:
        calc_feature(key,file)
