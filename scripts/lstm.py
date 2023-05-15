import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, Flatten, LSTM#, CuDNNLSTM
import numpy as np
import datetime

with np.load('game_data.npz') as f:
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

model = Sequential()

model.add(Flatten())

#model.add(Dense(256, activation='relu'))

#model.add(Dense(128, activation='relu'))

model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(2, activation='softmax'))


# Compile model
model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy'],
)

log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

model.fit(x_train,
          y_train,
          epochs=1000,
          batch_size=32,
          validation_data=(x_test, y_test),callbacks=[tensorboard_callback])