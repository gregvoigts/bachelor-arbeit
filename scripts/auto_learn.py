import autosklearn.classification
import sklearn.metrics
import numpy as np

with np.load('game_data_champs_only.npz') as f:
    data_x = f['x']
    data_y = f['y']

red = 0
blue = 0
for val in data_y:
    red += val[1]
    blue += val[0]

print(data_y.shape)
print(f'red:{red} blue:{blue}')

x_train, x_test = np.split(data_x,[int(.9 * len(data_x))])
y_train, y_test = np.split(data_y,[int(.9 * len(data_y))])

print(x_train.shape)
print(x_train[0].shape)

print(y_train.shape)
print(y_train[0].shape)

automl = autosklearn.classification.AutoSklearnClassifier(memory_limit=8192, initial_configurations_via_metalearning=25)
automl.fit(x_train, y_train)
y_hat = automl.predict(x_test)
print("Accuracy score", sklearn.metrics.accuracy_score(y_test, y_hat))