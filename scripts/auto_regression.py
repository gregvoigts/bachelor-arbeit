import json
import pickle
import autosklearn.regression
import autosklearn.metrics
import sklearn.metrics
from sklearn.model_selection import train_test_split
import numpy as np
from pprint import pprint
import pandas as pd
import random

def threshold_metric(y,y_hat):
    scores = []
    thresholds = np.linspace(0,1,100)
    y_binary = [random.choices([0,1],[1-v,v]) for v in y]
    for threshold in thresholds:
        y_pred = np.where(y_hat>=threshold, 1, 0)
        scores.append(sklearn.metrics.accuracy_score(y_binary,y_pred))
    return pd.DataFrame(zip(thresholds,scores),columns=['Threshold','Score'])

def auto_regression(folder):
    folder = f'regression/{folder}'
    # Load dataset
    with np.load(f'{folder}/game_data.npz') as f:
        data_x = f['x']
        data_y = f['y']

    # calculate blue and red side wins
    red = 0
    blue = 0
    for val in data_y:
        red += 1-val
        blue += val
    print(f'red:{red} blue:{blue}')

    # split data into train and test set
    # x_train, x_test = np.split(data_x,[int(.9 * len(data_x))])
    # y_train, y_test = np.split(data_y,[int(.9 * len(data_y))])
    x_train,x_test,y_train,y_test = train_test_split(data_x,data_y,test_size=0.2, random_state=42)
    print(x_train.shape)
    print(y_train.shape)

    # create classifier
    automl = autosklearn.regression.AutoSklearnRegressor(memory_limit=8192, time_left_for_this_task=1800, metric=autosklearn.metrics.r2)
    # fit classifier to data
    automl.fit(x_train, y_train)

    # predict test and train set
    y_hat_test = automl.predict(x_test)
    y_hat_train = automl.predict(x_train)

    # calculate accuracy
    acc = threshold_metric(y_test, y_hat_test)
    train_acc = threshold_metric(y_train, y_hat_train)

    best_acc = acc.loc[acc['Score'].idxmax()]
    best_train_acc = train_acc.loc[acc['Score'].idxmax()]
    print("Accuracy score", best_acc)
    print("Train Accuracy score", best_train_acc)

    # store classifier obj
    with open(f'{folder}/classifier.pkl', 'wb') as f:
        pickle.dump(automl, f)

    # write out results
    with open(f'{folder}/result.txt','w') as f:
        f.write(f'red:{red}\nblue:{blue}({blue/(red+blue)}%)\n')
        f.write(f'Accuracy: {best_acc}\n')
        f.write(f'Train Accuracy: {best_train_acc}\n')

    acc.to_csv(f'{folder}/acc_threshold.csv')

    automl.leaderboard().to_csv(f'{folder}/leaderboard.csv')

    with open(f'{folder}/models.txt','w') as f:
        pprint(automl.show_models(),indent=4,stream=f)
