import sklearn_crfsuite as crf
import subprocess
import sys
import numpy as np
import pycrfsuite
from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix
from collections import defaultdict

import itertools
import pickle
from itertools import chain

import nltk
import sklearn
import scipy.stats
from sklearn.metrics import make_scorer
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import RandomizedSearchCV

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics

DELTA = 3
SPACE_DIMS = 26**DELTA

# Input: a string e.g. "drivers"
# Output: a matrix n_chars X SPACE_DIM, a vector of target values
def tag_word(word, target, delta):
    word = "^{}$".format(word)
    target = target.split(",")[0] #  multiple annotations
    morphs = ["^"]
    morphs.extend([string.split(":")[0] for string in target.split(" ")])
    morphs.append("$")

    # data_size = (sum([len(morph) for morph in morphs]), SPACE_DIMS)
    dimensions = set()
    # xs = csr_matrix(data_size, dtype=np.bool)
    # labels_size = (data_size[0], 1)
    # ys = np.zeros(labels_size, dtype=np.uint8)
    # offset = 0
    xs = []
    ys = []
    tags = []
    for morph in morphs:
        tags.extend(tag_morph(morph))

    print(word)
    for letter_idx, letter in enumerate(word):
        x = letter_to_dict(word, letter, letter_idx, delta)
        print(tags[letter_idx], letter, dict(x))

    print(word)
    for letter_idx, letter in enumerate(word):
        x = letter_to_dict(word, letter, letter_idx, delta)
        print(tags[letter_idx], letter, dict(x))

        dimensions.update(x.keys())
        xs.append(x)

    if len(xs) != len(tags):
        good_tags = [tag for tag in tags if tag != "~"]
        good_tags = good_tags[0:len(xs)-1] + [good_tags[-1]]
        print(good_tags, tags, word, morphs)
        tags = good_tags
    return xs, dimensions, tags

def letter_to_dict(word, letter, letter_idx, delta):
    x = defaultdict(lambda: 0)
    x[letter] = 1
    for sub_morph in gen_submorphs(word, letter_idx, delta):
        x[sub_morph] = 1
    return x

def letter_to_vec(letter, morph, letter_idx, delta):
    size = (1, SPACE_DIMS)
    x = csr_matrix(size, dtype=np.bool)
    x[0, str_to_id(letter)] = True

    for sub_morph in gen_submorphs(morph, letter_idx, delta):
        # print("sub_morph", sub_morph)
        x[0, str_to_id(sub_morph)] = True
    return x

def gen_submorphs(word, letter_idx, delta):
    letter = word[letter_idx]
    before = word[:letter_idx]
    after = word[letter_idx + 1:]
    before_acc = ""  # letter
    after_acc = ""  # letter
    yield letter

    for b in reversed(before[-delta:]):
        before_acc = b + before_acc
        yield before_acc + "_"

    for a in after[:delta]:
        after_acc = after_acc + a
        yield "_" + after_acc
        # also skip 1 char

def str_to_id(string):
    return abs(hash(string)) % SPACE_DIMS

def tag_morph(morph):
    if morph == "^":
        return ["START"]

    if morph == "$":
        return ["STOP"]

    morph = list(morph)
    morph_tags = []


    if len(morph) == 1:
        morph_tags.append("S")
    else:
        morph_tags.append("B")
        for _ in morph[1:-1]:
            morph_tags.append("M")
        morph_tags.append("E")
    return morph_tags


def load_dataset(delta):
    # dataset_path = "task1_data/training.eng.txt"
    dataset_path = "task1_data/training.eng.txt"
    # wc_c = int(subprocess.check_output("awk '{print $1}' " + dataset_path + " | wc -c", shell=True)[:-1])
    # size = (wc_c, SPACE_DIMS)
    # xs = csr_matrix(size, dtype=np.bool)
    # ys = np.zeros(shape=(xs.shape[0], 1), dtype=np.uint8)
    # offset = 0
    dimensions = set()
    small_xs = []
    ys = []
    with open(dataset_path) as fin:
        for row in fin:
            print(row[:-1])
            word, target = row[:-1].split("\t")
            x, word_dims, y = tag_word(word, target, delta)
            dimensions.update(word_dims)
            # print("[RETR] tag_word({}, {})".format(target, delta))
            small_xs.append(x)
            ys.append(y)
            # xs[offset: offset + x.shape[0]] = x
            # ys[offset: offset + y.shape[0]] = y
            # if row[0] == 'b': break
    print("xs", len(small_xs), "ys", len(ys))
    print("xs", len(small_xs[0]), "ys", len(ys[0]))
    print("expanding")
    # xs = []
    # while(small_xs):
    #     small_x = small_xs.pop()
    #     for sx in small_x:
    #         x = {}
    #         for dim in dimensions:
    #             x[dim] = small_x[dim]
    #         x = small_x
    #         xs.append(x)
    print("done")
    return small_xs, dimensions, ys

def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
            '-1:postag': postag1,
            '-1:postag[:2]': postag1[:2],
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
            '+1:postag': postag1,
            '+1:postag[:2]': postag1[:2],
        })
    else:
        features['EOS'] = True

    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]

def optimize_delta(training_set, test_set):
    for _ in range(ITERATIONS):
        for word in training_set:
            word = "^{}$".format(word)
            model.train(blablabla)

    print(eval_model(model, test_set))

def tag_to_id(tag):
    tags = [
        'START',
        'B',
        'M',
        'E',
        'S',
        'STOP',
    ]
    return tags.index(tag)

try:
    del x
    del y
except:
    pass

X, dimensions, Y = load_dataset(delta=DELTA)
model = crf.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True,
        verbose=True,
)

model.fit(X, Y)
test_word = "^{}$".format("augmented")
print("predict", test_word)
for letter in test_word:
    print(letter, end="\t")
print("")
for letter_idx, letter in enumerate(test_word):
    x = {}
    small_x = letter_to_dict(test_word, letter, letter_idx, DELTA)
    for dim in dimensions:
        x[dim] = small_x[dim]
    for klass in model.predict([[x]]):
        print(klass, end="\t")
