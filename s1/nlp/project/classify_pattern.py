import glob
import string
import gensim
import os
from keras.models import Sequential
from keras.layers import GRU
import difflib
from sklearn.preprocessing import normalize
import pickle
import nltk
# import hw2
import numpy as np
from utils import disk_cache


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not hasattr(self, 'model'):
            self.model = None

    def load_resource(self):
        if not self.model:
            w2v_path = "/home/awok/Documents/sapienza/s1/nlp/project/../hw2/resources/model.w2v"
            self.model = gensim.models.Word2Vec.load(w2v_path, mmap='r')

    def __getitem__(self, item):
        self.load_resource()
        return self.model.__getitem__(item)


with open("chatbot_maps/domains_to_relations.tsv") as fin:
    # Philosophy and psychology	activity	similarity	time	generalization	size	specialization	part
    domain_list = []
    for row in fin:
        domain_list.extend(row.strip("\n").lower().split("\t")[1:])
    domain_list = set(domain_list)
    domain_list.remove("")

np.random.seed(42)
UNKNOWN_SYMBOL = np.random.rand(300)
PUNKT_SYMBOL = np.random.rand(300)
SYMBOL_SYMBOL = np.random.rand(300)

UNKNOWN_SYMBOL -= UNKNOWN_SYMBOL.mean()
PUNKT_SYMBOL -= PUNKT_SYMBOL.mean()
SYMBOL_SYMBOL -= SYMBOL_SYMBOL.mean()


@disk_cache
def to_vector(word):
    model = Borg()
    word = word.lower()
    try:
        return model[word]
    except KeyError:
        if word in "\"\'(),.[]`:":
            return PUNKT_SYMBOL
        elif word in string.punctuation:
            return SYMBOL_SYMBOL
        return UNKNOWN_SYMBOL


def train_lstm():
    targets = load_data()

    target_lookup = list(set(targets))
    batch_size = 128
    lstm_hidden_dims = 32
    output_dim = len(target_lookup)

    model = Sequential()
    # model.add( Bidirectional(LSTM(lstm_hidden_dims, dropout=0.2, recurrent_dropout=0.2), input_shape=x_train.shape[1:], ))
    # , return_sequences=True
    # model.add(Dense(4, ))

    model.add(GRU(lstm_hidden_dims, dropout=0.2, recurrent_dropout=0.2, input_shape=x_train.shape[1:], ))
    # model.add(Bidirectional(GRU(lstm_hidden_dims, dropout=0.2, recurrent_dropout=0.2), input_shape=x_train.shape[1:]))
    model.add(Dense(output_dim, activation='sigmoid'))  # try sigmoid

    model.compile(loss='categorical_crossentropy', optimizer="adam", metrics=['accuracy'])

    print(model.summary())
    plot_model(model, to_file='model.png')
    print('Train...')
    history = model.fit(x_train, y_train, validation_data=(x_val, y_val), batch_size=batch_size, shuffle=True,
                        epochs=10)
    model.save("classify_pattern.keras")

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


def load_data():
    words = []
    targets = []
    for file_name in glob.glob("patterns/*"):
        print("FILE:", file_name)
        with open(file_name) as fin:
            for row in fin:
                try:
                    question, target = parse_row(row)
                except ValueError:
                    continue
                question = [to_vector(word) for word in question]
                words.extend(question)
                targets.extend(target)

                # from keras.utils import to_categorical
                # sentences = [[to_vector(model, word['form']) for word in sentence] for sentence in data]
                # labels = [[to_label(word['upostag']) for word in sentence] for sentence in data]
                # padding = to_vector(model, "padding")

                # xs, ys = add_context(sentences, labels, padding)
                # xs = np.array(xs)
                # ys = to_categorical(np.array(ys), 17)
                # with open(training_path + ".pkl", "wb") as f:
                #     pickle.dump((xs, ys), f)
                # return xs, ys
    return targets


def frequency_matrix():
    words = []
    targets = []
    for file_name in glob.glob("patterns/*"):
        print("FILE:", file_name)
        with open(file_name) as fin:
            for row in fin:
                try:
                    question, target = parse_row(row)
                except ValueError:
                    continue
                words.extend(question)
                targets.extend([target] * len(question))
    encoded = list(set(words))
    lookup = {e: idx for idx, e in enumerate(encoded)}
    tags = list(set(targets))
    matrix = np.zeros(shape=(len(encoded), len(tags)))
    for word, target in zip(words, targets):
        word = lookup[word]
        target = tags.index(target)
        matrix[word][target] += 1
    norm_matrix = normalize(matrix, axis=0, norm='l1')
    return lookup, tags, norm_matrix


def parse_row(entry):
    entry = entry.strip("\n").lower()
    if "\t" not in entry:
        print("SKIPPING", entry)
        raise ValueError()
    question, target = entry.split("\t")
    target = target.strip()
    target = target.strip("\"\'")
    question = question.strip()
    question = question.strip("\"\'")
    if "?" in target:
        question, target = target, question
    question = nltk.tokenize.word_tokenize(question)
    sno = nltk.stem.SnowballStemmer('english')
    question = [sno.stem(word) for word in question]
    if target not in domain_list:
        # raises ValueError if no close match
        new_target, = difflib.get_close_matches(target, domain_list, n=1)
        print(target, "not in domain list => ", new_target)
        target = new_target
    return question, target


def find_relation(question):
    lookup, tags, matrix = load_state()

    question_vec = np.zeros(shape=matrix[0].shape)
    for word in question:
        try:
            word = lookup[word]
            question_vec += matrix[word] / matrix[word].sum()
        except KeyError:
            pass
    # target = tags.index(target_hat)
    # print(question)
    target = None
    for score, tag in zip(question_vec, tags):
        cutoff = np.sort(question_vec)[-5]
        if score > cutoff:
            if score == question_vec.max():
                # print(tag, "***" + str(score) + "**" )
                target = tag
            else:
                pass
                # print(tag, score)
    return target


def main():
    print("training lstm")
    train_lstm()
    print("trained lstm")
    """
    # WARNING: STEMMING REDUCES ACCURACY BY 5%
    good_guesses = 0
    total = 0
    for file_name in glob.glob("patterns/*"):
        print("FILE:", file_name)
        with open(file_name) as fin:
            for row in fin:
                try:
                    question, target_hat = parse_row(row)
                except ValueError:
                    continue
                else:
                    target = find_relation(question)
                    if target == target_hat:
                        good_guesses += 1
                    else:
                        print("WRONG: was ", target_hat, "guessed: ", target)
                    total += 1
                    print(good_guesses / total, "-" * 500)
    """


def load_state():
    global lookup, tags, matrix
    try:
        return lookup, tags, matrix
    except NameError as e:
        cache_file = "cache/classify_pattern.pkl"
        try:
            with open(cache_file, "rb") as fout:
                lookup, tags, matrix = pickle.load(fout)
        except IOError as e:
            lookup, tags, matrix = frequency_matrix()
            with open(cache_file, "wb") as fout:
                pickle.dump((lookup, tags, matrix), fout)
        return lookup, tags, matrix


if __name__ == "__main__":
    main()
