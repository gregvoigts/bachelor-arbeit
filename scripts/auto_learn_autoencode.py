import json
import pickle
import autosklearn.classification
import sklearn.metrics
import numpy as np
from pprint import pprint
from sklearn.decomposition import PCA
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split

def auto_learn_encoded(folder):
    # Folder for specific Dataset
    folder = f'classifier/{folder}'

    # Load dataset
    with np.load(f'{folder}/game_data.npz') as f:
        data_x = f['x']
        data_y = f['y']

    # load the model from file
    encoder = load_model('encoder.h5')

    # run PCA to reduce sparse champion matrix
    only_champs,other = np.array_split(data_x,[163],axis=1)
    reduced = encoder.predict(only_champs)
    transformed_X = np.concatenate((reduced,other),axis=1)

    # calculate blue and red side wins
    red = 0
    blue = 0
    for val in data_y:
        red += 1-val
        blue += val
    print(f'red:{red} blue:{blue}')

    # split data into train and test set
    x_train,x_test,y_train,y_test = train_test_split(transformed_X,data_y,test_size=0.2, random_state=42)
    print(x_train.shape)
    print(y_train.shape)

    # create classifier
    automl = autosklearn.classification.AutoSklearnClassifier(memory_limit=8192,time_left_for_this_task=3600, initial_configurations_via_metalearning=25,)
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
    with open(f'{folder}/classifier_autoencode.pkl', 'wb') as f:
        pickle.dump(automl, f)

    # write out results
    with open(f'{folder}/result_autoencode.txt','w') as f:
        f.write(f'red:{red}\nblue:{blue}({blue/(red+blue)}%)\n')
        f.write(f'Accuracy: {acc}\n')
        f.write(f'Train Accuracy: {train_acc}\n')

    automl.leaderboard().to_csv(f'{folder}/leaderboard_autoencode.csv')

    with open(f'{folder}/models_autoencode.txt','w') as f:
        pprint(automl.show_models(),indent=4,stream=f)