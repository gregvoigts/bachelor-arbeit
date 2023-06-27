# train autoencoder for classification with with compression in the bottleneck layer
from sklearn.datasets import make_classification
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.utils import plot_model
import numpy as np

# load data
with np.load(f'classifier/all_games_champs_only/game_data.npz') as f:
    data_x = f['x']
    data_y = f['y']

# split data into train and test set
x_train,x_test,y_train,y_test = train_test_split(data_x,data_y,test_size=0.2, random_state=42)
n_inputs = data_x.shape[1]

# define encoder
visible = Input(shape=(n_inputs,))
# encoder level 1
e = Dense(n_inputs*2)(visible)
e = BatchNormalization()(e)
e = LeakyReLU()(e)
# encoder level 2
e = Dense(n_inputs)(e)
e = BatchNormalization()(e)
e = LeakyReLU()(e)
# bottleneck
n_bottleneck = round(float(n_inputs) / 2.0)
bottleneck = Dense(n_bottleneck)(e)
# define decoder, level 1
d = Dense(n_inputs)(bottleneck)
d = BatchNormalization()(d)
d = LeakyReLU()(d)
# decoder level 2
d = Dense(n_inputs*2)(d)
d = BatchNormalization()(d)
d = LeakyReLU()(d)
# output layer
output = Dense(n_inputs, activation='linear')(d)
# define autoencoder model
model = Model(inputs=visible, outputs=output)
# compile autoencoder model
model.compile(optimizer='adam', loss='mse')
# fit the autoencoder model to reconstruct input
history = model.fit(x_train, x_train, epochs=200, batch_size=16, verbose=2, validation_data=(x_test,x_test))
# define an encoder model (without the decoder)
encoder = Model(inputs=visible, outputs=bottleneck)
encoder.compile(optimizer='adam', loss='mse')
# save the encoder to file
encoder.save('encoder.h5')