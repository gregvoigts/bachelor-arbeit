from sklearn.inspection import permutation_importance
import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from tinydb import Query, TinyDB
import matplotlib.pyplot as plt

folder = 'classifier/europe_games_full'

file = 'classifier.pkl'

# init champion DB with all champions and winrates per date
champ_db = TinyDB('champs.json')
ChampQ = Query()

champ_db.all()

feature_names = [doc['name'] for doc in champ_db.all()]

stats = ['champwr','prowr','gold','kills','dmg','deaths']

pos = ['top_blue','jng_blue','mid_blue','bot_blue','sup_blue','top_red','jng_red','mid_red','bot_red','sup_red']

for p in pos:
    for s in stats:
        feature_names.append(f'{p}_{s}')

with np.load(f'{folder}/game_data.npz') as f:
    data_x = f['x']
    data_y = f['y']

x_train, x_test = np.split(data_x,[int(.9 * len(data_x))])
y_train, y_test = np.split(data_y,[int(.9 * len(data_y))])
#x_train,x_test,y_train,y_test = train_test_split(data_x,data_y,test_size=0.2, random_state=42)

with open(f'{folder}/{file}','rb') as f:
    classi = pickle.load(f)

result = permutation_importance(
    classi, x_test, y_test, n_repeats=10, random_state=42, n_jobs=2
)


importances = pd.Series(result.importances_mean, index=feature_names) # type: ignore

plt.figure(num=None,figsize=(100,100),dpi=80,facecolor='w',edgecolor='k')
fig, ax = plt.subplots()
importances.plot.bar(yerr=result.importances_std, ax=ax) # type: ignore
ax.set_title("Feature importances using permutation on full model")
ax.set_ylabel("Mean accuracy decrease")
fig.tight_layout()
plt.show()