from auto_learn import auto_learn
from auto_regression import auto_regression
from auto_learn_autoencode import auto_learn_encoded
folders = ['from_costaetal_self_org']


for folder in folders:
    try:
        auto_learn(folder)
    except Exception as e:
        print(f'error in folder {folder}')
        print(e)