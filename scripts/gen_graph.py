import matplotlib.pyplot as plt
import pandas as pd

def addlabels(ax):
    for p in ax.patches:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        ax.annotate(f'{height}', (x + width/2, y + height), ha='center')


def plot_data(df):
    ax = df.plot.bar(x='Dataset',y='Number', title ="Accuracy for Regression", fontsize=12, legend = False)
    ax.set_ylabel("Accuracy", fontsize=12)
    addlabels(ax)
    plt.show()

def plt_pivot(df):
    pivot = df.pivot(index='Dataset',columns='Model',values='Number')
    ax = pivot.plot.bar(title ="Accuracy for diffrent champion encodings", fontsize=12, legend = True,figsize=(20,5))
    ax.set_ylabel("Accuracy", fontsize=12)
    addlabels(pivot)
    plt.show()

reg_data = pd.read_csv('flask/static/data/result_complete_regression.csv',delimiter=';',decimal=',')
classi_data = pd.read_csv('flask/static/data/result_complete_classifier.csv',delimiter=';',decimal=',')

filtered_reg = reg_data.loc[reg_data['Value'] == 'Accuracy']
filtered_classi = classi_data.loc[classi_data['Dataset'].isin(['all_games_champ_stats_only','all_games_champs_only','all_games_matchups','all_games_simple_v2'])]

