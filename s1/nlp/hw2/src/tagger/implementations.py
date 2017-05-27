import conllu.parser
from keras.utils import plot_model
import matplotlib.pyplot as plt
import keras.models
from keras.layers import Dense
from keras.layers import GRU, Embedding, Bidirectional
from keras.models import Sequential

import string
import os
import gc
import re
import gensim
import numpy as np
import pickle

# labels_lookup = []
np.random.seed(42)
UNKNOWN_SYMBOL = np.random.rand(300)
PUNKT_SYMBOL = np.random.rand(300)
SYMBOL_SYMBOL = np.random.rand(300)

UNKNOWN_SYMBOL -= UNKNOWN_SYMBOL.mean()
PUNKT_SYMBOL -= PUNKT_SYMBOL.mean()
SYMBOL_SYMBOL -= SYMBOL_SYMBOL.mean()


def to_vector(model, word):
    # return np.random.randn(300)
    word = word.lower()
    try:
        return model[word]
    except KeyError:
        if word in "\"\'(),.[]`:":
            return PUNKT_SYMBOL
        elif word in string.punctuation:
            return SYMBOL_SYMBOL
        # # retr = np.zeros(shape=model['cake'].shape)
        # subwords = []
        # for subword in reversed(sorted(re.split("[^\w]+", word), key=len)):
        #     try:
        #         retr = model[subword]
        #         subwords.append(retr)
        #     except KeyError:
        #         pass
        # if subwords:
        #     return np.array(subwords).mean(axis=0)
        # else:
        #     # wget synonims from bablenet
        return UNKNOWN_SYMBOL


def to_label(word):
    return ['ADJ', 'ADP', 'ADV', 'AUX', 'CONJ', 'DET', 'INTJ', 'NOUN', 'NUM',
            'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X'].index(word)


def add_context(sentences, labels, padding):
    print("add_context", len(sentences))
    xs = []
    ys = []
    for sentence, sentence_labels in zip(sentences, labels):
        for word_idx, (word, label) in enumerate(zip(sentence, sentence_labels)):
            word_and_context = ([padding] * 2 + sentence + [padding] * 2)[word_idx: word_idx + 4]
            xs.append(word_and_context)
            ys.append(label)
    return xs, ys


def add_context_single(sentence, padding):
    xs = []
    for word_idx, word in enumerate(sentence):
        word_and_context = ([padding] * 2 + sentence + [padding] * 2)[word_idx: word_idx + 4]
        xs.append(word_and_context)
    return xs


def load_data(training_path):
    print("load_data", training_path)
    try:
        with open(training_path + ".pkl", "rb") as f:
            return pickle.load(f)
    except IOError:
        print("cached model for {} failed".format(training_path))

    with open(training_path) as fin:
        data = conllu.parser.parse(fin.read())

    model = Borg()
    # gensim.models.Word2Vec.load("/home/awok/Documents/sapienza/s1/nlp/hw2/resources/model.w2v", mmap='r')

    from keras.utils import to_categorical
    sentences = [[to_vector(model, word['form']) for word in sentence] for sentence in data]
    labels = [[to_label(word['upostag']) for word in sentence] for sentence in data]
    padding = to_vector(model, "padding")

    xs, ys = add_context(sentences, labels, padding)
    xs = np.array(xs)
    ys = to_categorical(np.array(ys), 17)
    # with open(training_path + ".pkl", "wb") as f:
    #     pickle.dump((xs, ys), f)
    return xs, ys


def train(training_path):
    print("train", training_path)
    x_train, y_train = load_data(training_path)
    print(len(x_train), 'train sequences')
    x_val, y_val = load_data(training_path.replace("train", "dev").replace("_original", ""))

    batch_size = 128
    #                   V increase to 128/2 if needed
    lstm_hidden_dims = 32

    model = Sequential()
    # model.add( Bidirectional(LSTM(lstm_hidden_dims, dropout=0.2, recurrent_dropout=0.2), input_shape=x_train.shape[1:], ))
    # , return_sequences=True
    # model.add(Dense(4, )

    # model.add(GRU(lstm_hidden_dims, dropout=0.2, recurrent_dropout=0.2, input_shape=x_train.shape[1:], ))
    model.add(Bidirectional(GRU(lstm_hidden_dims, dropout=0.2, recurrent_dropout=0.2), input_shape=x_train.shape[1:]))
    model.add(Dense(17, activation='sigmoid'))  # try sigmoid

    model.compile(loss='categorical_crossentropy',
                  optimizer="adam",
                  metrics=['accuracy'])

    print(model.summary())
    plot_model(model, to_file='model.png')
    print('Train...')
    history = model.fit(x_train, y_train,
                        validation_data=(x_val, y_val),
                        batch_size=batch_size,
                        shuffle=True,
                        epochs=10)
    print(history.history.keys())
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('history_accuracy.jpg')
    plt.clf()
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('history_loss.jpg')
    # model.save("trained_model.keras")
    return model


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not hasattr(self, 'model'):
            self.model = None

    def load_resource(self, resources_path):
        if not self.model:
            w2v_path = os.path.join(resources_path, "word-vectors-english")
            print("BORG: IM GOING TO LOAD! BEWARE! ", w2v_path)
            try:
                self.model = gensim.models.Word2Vec.load_word2vec_format(w2v_path, binary=True)
            except FileNotFoundError:  # my conputer cannot handle the full w2v :(
                w2v_path = os.path.join(resources_path, "model.w2v")
                self.model = gensim.models.Word2Vec.load(w2v_path, mmap='r')

    def __getitem__(self, item):
        return self.model.__getitem__(item)


def to_tag(predictions):
    return [['ADJ', 'ADP', 'ADV', 'AUX', 'CONJ', 'DET', 'INTJ', 'NOUN', 'NUM',
             'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X'][np.argmax(prediction)] for prediction in
            predictions]

