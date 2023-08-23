import os
import re
import pandas as pd

f = open('./leaderboards.txt','w')

def handle_file(method,dataset,version):
    leaderboard = pd.read_csv(f'{method}/{dataset}/leaderboard{version}.csv')
    leaderboard = leaderboard.drop('duration', axis=1)
    leaderboard = leaderboard.drop('model_id', axis=1)

    leaderboard = leaderboard.round(3)

    tabular = leaderboard.style.format(precision=3).to_latex().replace('_','-')

    table = '''
    \\begin(table)[]
        \\centering
        {}
        \\caption({})
        \\label(tab:{})
    \\end(table)'''

    final = table.format(tabular,f'Leaderboard for the ensemble model trained with the {dataset} dataset',f'lb_{dataset}{version}').replace('(','{').replace(')','}')

    f.write(final)
    f.write('\n')

methods = ['classifier','regression']
pattern = r'^leaderboard(_PCA_30).csv'
for method in methods:
    for root, dirs, files in os.walk(f'./{method}'):
        for directory in dirs:
            folder_path = os.path.join(root, directory)
            for file in os.listdir(folder_path):
                match = re.match(pattern,file)
                if match:
                    handle_file(method,directory,match.group(1))

f.close()