import numpy as np
import pickle
import sklearn.metrics


folder = 'classifier/lec_games_full'

with np.load(f'{folder}/game_data.npz') as f:
    data_x = f['x']
    data_y = f['y']

red = 0
blue = 0
for val in data_y:
    #red += 1-val
    #blue += val
    red += val[1]
    blue += val[0]

print(data_y.shape)
print(f'red:{red} blue:{blue}')

x_train, x_test = np.split(data_x,[int(.9 * len(data_x))])
y_train, y_test = np.split(data_y,[int(.9 * len(data_y))])

with open(f'{folder}/classifier.pkl','rb') as f:
    classi = pickle.load(f)

y_hat_test = classi.predict(x_test)
y_hat_train = classi.predict(x_train)
print(y_hat_test)
acc = sklearn.metrics.accuracy_score(y_test, y_hat_test)
train_acc = sklearn.metrics.accuracy_score(y_train, y_hat_train)

with open(f'{folder}/result.txt','w') as f:
    f.write(f'red:{red}\nblue:{blue}({blue/(red+blue)}%)\n')
    f.write(f'Accuracy: {acc}\n')
    f.write(f'Train Accuracy: {train_acc}\n')