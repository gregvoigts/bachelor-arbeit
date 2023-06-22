import json
import pickle
import autosklearn.classification
import sklearn.metrics
import numpy as np
from pprint import pprint
from sklearn.decomposition import PCA

# executes a PCA on the input dataset and returns result
def pca(sample:np.ndarray):
    pca = PCA(n_components=30)
    return pca.fit_transform(sample)

# Folder for specific Dataset
folder = 'classifier/europe_games_full'

# Load dataset
with np.load(f'{folder}/game_data.npz') as f:
    data_x = f['x']
    data_y = f['y']

# run PCA to reduce sparse champion matrix
only_champs,other = np.array_split(data_x,[163],axis=1)
reduced = pca(only_champs)
transformed_X = np.concatenate((reduced,other),axis=1)

# calculate blue and red side wins
red = 0
blue = 0
for val in data_y:
    red += 1-val
    blue += val
print(f'red:{red} blue:{blue}')

# split data into train and test set
x_train, x_test = np.split(transformed_X,[int(.9 * len(transformed_X))])
y_train, y_test = np.split(data_y,[int(.9 * len(data_y))])
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
with open(f'{folder}/classifier_PCA_30.pkl', 'wb') as f:
    pickle.dump(automl, f)

# write out results
with open(f'{folder}/result_PCA_30.txt','w') as f:
    f.write(f'red:{red}\nblue:{blue}({blue/(red+blue)}%)\n')
    f.write(f'Accuracy: {acc}\n')
    f.write(f'Train Accuracy: {train_acc}\n')

automl.leaderboard().to_csv(f'{folder}/leaderboard_PCA_30.csv')

with open(f'{folder}/models_PCA_30.txt','w') as f:
    pprint(automl.show_models(),indent=4,stream=f)