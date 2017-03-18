import sklearn_crfsuite as crf
from nltk.corpus import cmudict
import subprocess
import sys
import numpy as np
import pycrfsuite
from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix
from collections import defaultdict

from nltk.corpus import wordnet as wn

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

d = cmudict.dict()
DELTAS = range(14, 20)

def tag_word(word, target, delta):
    word = "^{}$".format(word)
    morphs = ["^"]
    morphs.extend([string.split(":")[0] for string in target.split(" ")])
    morphs.append("$")

    dimensions = set()
    xs = []
    ys = []
    tags = []
    for morph in morphs:
        tags.extend(tag_morph(morph))

    for letter_idx, letter in enumerate(word):
        x = letter_to_dict(word, letter, letter_idx, delta)
        dimensions.update(x.keys())
        xs.append(x)

    if len(xs) != len(tags):
        good_tags = [tag for tag in tags if tag != "~"]
        good_tags = good_tags[0:len(xs)-1] + [good_tags[-1]]
        tags = good_tags
    return xs, dimensions, tags

def letter_to_dict(word, letter, letter_idx, delta):
    x = {}
    for sub_morph in gen_submorphs(word, letter_idx, delta):
        x[sub_morph] = 1

    # def syl(word):
    #     return [list(y for y in x if y[-1].isdigit()) for x in d[word.lower()]]

    # try:
    #     for syls in syl(word[1:-1]):
    #         for syl in syls:
    #             x[syl] = 1
    # except KeyError as e:
    #     pass
    x['position'] = letter_idx
    #     # print("skipping syl", e)
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
    yield word

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
        for idx, _ in enumerate(morph[1:-1]):
            morph_tags.append("M")
        morph_tags.append("M")
        # morph_tags.append("E")
    return morph_tags


def load_dataset(dataset_path, delta):
    # wc_c = int(subprocess.check_output("awk '{print $1}' " + dataset_path + " | wc -c", shell=True)[:-1])
    # size = (wc_c, SPACE_DIMS)
    # xs = csr_matrix(size, dtype=np.bool)
    # ys = np.zeros(shape=(xs.shape[0], 1), dtype=np.uint8)
    # offset = 0
    dimensions = set()
    small_xs = []
    ys = []
    words = set()
    with open(dataset_path) as fin:
        for row in fin:
            word, target = row[:-1].split("\t")
            target = target.split(",")[0] #  multiple annotations
            words.add(word)
            x, word_dims, y = tag_word(word, target, delta)
            small_xs.append(x)
            ys.append(y)

    if "train" in dataset_path and False:
        with open("/usr/share/dict/american-english") as fin:
            for row in fin:
                word = row[:-1]
                if len(word) > 3:
                    continue
                if len(word) == 1:
                    continue
                if "'" in word:
                    continue
                if word not in words:
                    small_xs.append(x)
                    ys.append(y)
                # # print(word)
                # target = row
                # if word not in words:
                #     x, word_dims, y = tag_word(word, target, delta)
                #     for letter_idx, letter in enumerate(x):
                #         for key in letter:
                #             if key != 'position':
                #                 x[letter_idx][key] /= 1
                #     small_xs.append(x)
                #     ys.append(y)

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

    # print(eval_model(model, test_set))

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
    del X_train
except:
    pass

for delta in DELTAS:
    print("load")
    X_train, dimensions, y_train = load_dataset("task1_data/training.eng.txt", delta=delta)
    model = crf.CRF(
            algorithm='ap',
            # algorithm='lbfgs',
            # c1=0.1,
            # c2=0.01,
            max_iterations=500,
            all_possible_transitions=True,
            verbose=False
    )
    print("fit")
    model.fit(X_train, y_train)

    labels = model.classes_
    # labels.remove("START") labels.remove("STOP")
    print("[SCORING] delta", delta)
    print("load")
    X_test, dimensions, y_test = load_dataset("task1_data/dev.eng.txt", delta=delta)
    print("predict")
    y_predicted = model.predict(X_test)
#    for word, yps, yts in zip(X_test, y_predicted, y_test):
#        try:
#            for letter, yp, yt in zip(word, yps, yts):
#                words = [word for word in letter if "^" in word and "$" in word]
#                if yp != yt:
#                    print(words)
#                    # words = [word for word in letter if "^" in word and "$" in word]
#                    print("\nguessed:")
#                    for y, letter in zip(yps, words[0]):
#                        # import ipdb; ipdb.set_trace()
#                        if y in ('B', 'S'):
#                            print("\t", end='')
#                        print(letter, end='')
#                    print("\nwas:")
#                    for y, letter in zip(yts, words[0]):
#                        # import ipdb; ipdb.set_trace()
#                        if y in ('B', 'S'):
#                            print("\t", end='')
#                        print(letter, end='')
#                    print("\npredicted")
#                    for y in yps: print(y, end='\t')
#                    print("\ntest")
#                    for y in yts: print(y, end='\t')
#                    print("")
#                    raise ValueError
#        except ValueError:
#            pass


    print(metrics.flat_classification_report(y_test, y_predicted, labels=labels, digits=3))
