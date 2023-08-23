import matplotlib.pyplot as plt
import pandas as pd

datasets_class = {'all_games_champs_only':'All games champions only',
 'all_games_champ_stats_only':'All games stats only',
 'all_games_matchups':'All games matchup',
 'all_games_pro_only':'Half year games pro stats',
 'all_games_pro_only_small':'Half year games limited pro stats',
 'all_games_pro_only_spring':'All games pro stats',
 'all_games_pro_only_spring_small':'All games limited pro stats',
 'all_games_simple_v2':'All games simple',
 'all_games_with_patch':'All games + patch',
 'all_games_with_region':'All games + region',
 'europe_games_full':'Europe soloqueue',
 'europe_games_full_champid':'Europe soloqueue + Champion Ids',
 'europe_games_simple':'Europe simple',
 'europe_games_stats_only':'Europe simple stats only',
 'from_costaetal':'Original Costa et.al.',
 'from_costaetal_self':'Like Costa et.al. more features',
 'from_costaetal_self_org':'Recreated exact Costa et.al.',
 'from_costaetal_self_small':'Like Costa et.al.',
 'lec_games_full':'LEC soloqueue',
 'lec_games_full_champid':'LEC soloqueue + Champion Ids',
 'lec_games_simple':'LEC simple'}

datasets_reg = {'all_games_champs_only':'All games champions only',
 'all_games_champ_stats_only':'All games stats only',
 'all_games_matchups':'All games matchup',
 'all_games_simple_v2':'All games simple'}

dataset_select_class = [
#
#  'all_games_champs_only',
#  'all_games_champ_stats_only',
#  'all_games_matchups',
#  'all_games_pro_only',
#  'all_games_pro_only_small',
 'all_games_pro_only_spring',
 'all_games_pro_only_spring_small',
#  'all_games_simple_v2',
#  'all_games_with_patch',
#  'all_games_with_region',
#  'europe_games_full',
#  'europe_games_full_champid',
#  'europe_games_pro_only',
#  'europe_games_simple',
#  'europe_games_stats_only',
#  'from_costaetal',
 'from_costaetal_self',
#  'from_costaetal_self_org',
 'from_costaetal_self_small',
#  'lec_games_full',
#  'lec_games_full_champid',
#  'lec_games_pro_only',
#  'lec_games_simple',
#
 ]

dataset_select_reg = [
#
 'all_games_champs_only',
 'all_games_champ_stats_only',
 'all_games_matchups',
 'all_games_simple_v2'
# 
]

model_select = [
#
'randsplit',
# 'normal',
# 'PCA',
# 'autoencode',
# 'PCA_30',
#
]

colors=['darkgray','gray','dimgray','lightgray']

is_reg = False

name = 'years'

def addlabels(ax):
    for p in ax.patches:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        ax.annotate(f'{height}', (x + width/2, y + height), fontsize=20, ha='center')

def plot_data(df):
    ax = df.plot.bar(x='Dataset',y='Number', title ="Accuracy for Regression", fontsize=15, legend = False,colors=colors)
    ax.set_ylabel("Accuracy", fontsize=12)
    addlabels(ax)
    plt.show()

def plt_pivot(df):
    pivot = df.pivot(index='Dataset',columns='Model',values='Number')
    ax = pivot.plot.bar(title ="", fontsize=22, legend = True,figsize=(10,8),color=colors)
    ax.set_ylabel("Accuracy", fontsize=19)
    addlabels(ax)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1),fontsize=16)
    plt.xticks(rotation=35)
    plt.tight_layout()
    plt.savefig(f'graphics/{name}.png')
    plt.show()

def map_names(value):
    if is_reg:
        return datasets_reg[value]
    return datasets_class[value]

def filter_datasets(df):
    if is_reg:
        return df.loc[df['Dataset'].isin(dataset_select_reg)]
    return df.loc[df['Dataset'].isin(dataset_select_class)]

if is_reg:
    #Load regression
    data = pd.read_csv('flask/static/data/result_complete_regression.csv',delimiter=';',decimal=',')
else:
    #Load classfier
    data = pd.read_csv('flask/static/data/result_complete_classifier.csv',delimiter=';',decimal=',')

data = data.loc[data['Value'] == 'Accuracy']

data = filter_datasets(data)

data = data.loc[data['Model'].isin(model_select)]

data['Dataset'] = data['Dataset'].apply(map_names)

plt_pivot(data)

