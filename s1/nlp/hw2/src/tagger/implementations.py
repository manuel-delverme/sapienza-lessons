import conllu.parser
import numpy as np
from keras.layers import Dense
from keras.layers import LSTM, Embedding
from keras.models import Sequential
from keras.preprocessing import sequence as ksequence
from keras.utils import to_categorical
import pickle

labels_lookup = []


def load_data(training_path):
    try:
        raise IOError
        with open(training_path + ".pkl", "rb") as f:
            return pickle.load(f)
    except IOError:
        with open(training_path) as fin:
            data = conllu.parser.parse(fin.read())

        def to_vector(word):
            return np.random.rand(300)

        def to_label(word):
            try:
                labels_lookup.index(word)
            except ValueError:
                labels_lookup.append(word)
            return labels_lookup.index(word)
            # retr = ([0] * 17)
            # try:
            #     retr[labels_lookup.index(word)] = 1
            # except ValueError:
            #     labels_lookup.append(word)
            #     retr[labels_lookup.index(word)] = 1
            # return retr

        x_train = [[to_vector(word['form']) for word in sentence] for sentence in data]
        y_train = [[to_label(word['upostag']) for word in sentence] for sentence in data]
    with open(training_path + ".pkl", "wb") as f:
        pickle.dump((x_train, y_train), f)
    return x_train, y_train


training_path = "/home/awok/Documents/sapienza/s1/nlp/hw2/data/en-ud-train.conllu"
max_sentence_length = 30  # cut texts after this number of words (among top max_features most common words)
batch_size = 32
#               V increase to 128 if needed
lstm_hidden_dims = 20

print('Loading data...')
x_train, y_train = load_data(training_path)
print(len(x_train), 'train sequences')

print('Pad sequences (samples x time)')
print('x_train shape: {} {} {}'.format(len(x_train), len(x_train[0]), len(x_train[0][0])))
x_train = ksequence.pad_sequences(x_train, maxlen=max_sentence_length)
print('x_train_padded shape:', x_train.shape)
# print('y_train shape: {} {} {}'.format(len(y_train), len(y_train[0]), len(y_train[0][0])))
# print('y_train shape:', y_train)
y_train = ksequence.pad_sequences(y_train, maxlen=max_sentence_length)
y_train_cat = to_categorical(y_train)
print('y_train_cat shape:', y_train_cat.shape)

print('Build model...')

model = Sequential()
model.add(LSTM(17, input_shape=x_train.shape[1:], dropout=0.2, recurrent_dropout=0.2))
# model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

print('Train...')
model.fit(x_train, y_train)
