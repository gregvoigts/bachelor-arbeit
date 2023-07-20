import re
import os
import json 
import pandas as pd
# reads all contents from a result file
# and returns a dict with all information
def read_result_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = r'([a-zA-Z]+\s?[a-zA-Z]+):\s?(\d+(?:\.\d+)?)'
    matches = re.findall(pattern, content)
    numbers_table = [[match[0], round(float(match[1]),2)] for match in matches]
    # calculate blueside winrate
    numbers_table[1][1] = numbers_table[1][1] / (numbers_table[0][1] + numbers_table[1][1])
    numbers_table[3][0] = numbers_table[3][0].replace(' ','_')
    numbers_table.pop(0)
    return numbers_table

# search a folder for all result.txt files
# returns map from result type and file path
def get_result_files(folder):
    pattern = r'(?:result)(?:_)?(.+)?(?:.txt)'
    res = []
    for file in os.listdir(folder):
        match = re.findall(pattern,file)
        if len(match) == 1:
            if match[0] == '':
                 match[0] = 'normal'
            res += [[match[0]] + line for line in read_result_file(os.path.join(folder,file))]
    return res


data = []
for root, dirs, files in os.walk('./classifier'):
        for directory in dirs:
            folder_path = os.path.join(root, directory)
            data += [[directory] + line for line in get_result_files(folder_path)]

df = pd.DataFrame(data,
                    columns=['Dataset', 'Model', 'Value', 'Number'])
df.to_csv('./flask/static/data/result_complete_classifier.csv',sep=';', decimal=',')
