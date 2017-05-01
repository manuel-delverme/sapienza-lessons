from keras.preprocessing import sequence as ksequence
from keras.preprocessing import text as preprocessing
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from gensim.models.keyedvectors import KeyedVectors
import conllu.parser
import keras.utils.np_utils
import numpy as np


class POSTaggerTrainer:
    def train(self, training_path):
        """
        Train the keras model from the training data.

        :param training_path: the path to training file
        :return: the keras model of type Sequential
        """
        '''Trains a LSTM on the IMDB sentiment classification task.
        The dataset is actually too small for LSTM to be of any advantage
        compared to simpler, much faster methods such as TF-IDF + LogReg.
        Notes:
        - RNNs are tricky. Choice of batch size is important,
        choice of loss and optimizer is critical, etc.
        Some configurations won't converge.
        - LSTM loss decrease patterns during training can be quite different
        from what you see with CNNs/MLPs/etc.
        '''

        max_sentence_length = 30  # cut texts after this number of words (among top max_features most common words)
        batch_size = 32

        print('Loading data...')
        x_train, y_train = self.load_data(training_path, max_words_in_sentence=max_sentence_length)
        print(len(x_train), 'train sequences')

        print('Pad sequences (samples x time)')
        x_train_padded = ksequence.pad_sequences(x_train, maxlen=max_sentence_length)
        print('x_train shape: {} {} {}'.format(len(x_train), len(x_train[0]), len(x_train[0][0])))
        print('x_train_padded shape:', x_train_padded.shape)

        # print(len(x_test), 'test sequences')
        # x_test = ksequence.pad_sequences(x_test, maxlen=maxlen)
        # print('x_test shape:', x_test.shape)

        print('Build model...')
        model = Sequential()
        # model.add(Embedding(max_features, 128))
        #               V increase to 128 if needed
        model.add(LSTM(20, input_shape=(max_sentence_length, 300), dropout=0.2, recurrent_dropout=0.2))
        model.add(Dense(1, activation='sigmoid'))

        # try using different optimizers and different optimizer configs
        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        print('Train...')
        x_test, y_test = self.load_data(training_path.replace("training", "development"),
                                        max_words_in_sentence=max_sentence_length)
        model.fit(x_train, y_train,
                  batch_size=1,
                  epochs=1, )
        # validation_data=(x_test, y_test))
        score, acc = model.evaluate(x_test, y_test,
                                    batch_size=batch_size)
        print('Test score:', score)
        print('Test accuracy:', acc)

    def load_data(self, training_path, max_words_in_sentence, max_words_dictionary=None):
        with open(training_path) as fin:
            data = conllu.parser.parse(fin.read())

        # texts = [" ".join([word['form'] for word in sentence]) for sentence in data]
        def to_vector(word):
            return np.random.rand(300)

        x_train = [[to_vector(word['form']) for word in sentence] for sentence in data]
        # labels = [" ".join([word['upostag'] for word in sentence]) for sentence in data]
        y_train = [[word['upostag'] for word in sentence] for sentence in data]
        # tokenizer = preprocessing.Tokenizer(num_words=max_words_dictionary)
        # tokenizer.fit_on_texts(texts)
        # print("parsed {} unique words".format(len(tokenizer.word_index)))

        # sequences = tokenizer.texts_to_sequences(texts)
        # x_train = ksequence.pad_sequences(sequences, maxlen=max_words_in_sentence)
        # word_vectors = KeyedVectors.load_word2vec_format(
        #     '/media/awok/CAE42B3EE42B2C5F/Users/Manuel/word2vec/GoogleNews-vectors-negative300.bin', binary=True)

        # y_train = keras.utils.np_utils.to_categorical(y=np.asarray(labels))

        return x_train, y_train

    def parse_sentence(self, idx, sentence):
        return []
