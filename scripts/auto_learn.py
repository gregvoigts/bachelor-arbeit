import json
import pickle
import autosklearn.classification
import sklearn.metrics
from sklearn.model_selection import train_test_split
import numpy as np
from pprint import pprint

def auto_learn(folder):
    folder = f'classifier/{folder}'
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
    automl = autosklearn.classification.AutoSklearnClassifier(memory_limit=8192, initial_configurations_via_metalearning=25)
    # fit classifier to data
    automl.fit(x_train, y_train)

    # predict test and train set
    y_hat_test = automl.predict(x_test)
    y_hat_train = automl.predict(x_train)

    # calculate accuracy
    acc = sklearn.metrics.accuracy_score(y_test, y_hat_test)
    train_acc = sklearn.metrics.accuracy_score(y_train, y_hat_train)
    print("Accuracy score", acc)
    print("Train Accuracy score", train_acc)

    # store classifier obj
    with open(f'{folder}/classifier_randsplit.pkl', 'wb') as f:
        pickle.dump(automl, f)

    # write out results
    with open(f'{folder}/result_randsplit.txt','w') as f:
        f.write(f'red:{red}\nblue:{blue}({blue/(red+blue)}%)\n')
        f.write(f'Accuracy: {acc}\n')
        f.write(f'Train Accuracy: {train_acc}\n')

    automl.leaderboard().to_csv(f'{folder}/leaderboard_randsplit.csv')

    with open(f'{folder}/models_randsplit.txt','w') as f:
        pprint(automl.show_models(),indent=4,stream=f)