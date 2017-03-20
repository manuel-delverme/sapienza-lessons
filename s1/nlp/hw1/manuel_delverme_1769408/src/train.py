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
import json

d = cmudict.dict()
DELTAS = range(1, 30)
UNIVERSAL_MODEL_LENGTH_MAX = 4
NOISE_LENGTH_COEFF = 4
USE_NOISE = True
FEATURE_WEIGHT = 1.0
KEEP_SELF = True
SELF_LEFT = True
SELF_RIGHT = True
NOTE_WORD = True
USE_E = False

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
        x[sub_morph] = FEATURE_WEIGHT

    # def syl(word):
    #     return [list(y for y in x if y[-1].isdigit()) for x in d[word.lower()]]

    # try:
    #     for syls in syl(word[1:-1]):
    #         for syl in syls:
    #             x[syl] = 1
    # except KeyError as e:
    #     pass
    #     # print("skipping syl", e)
    # x['position'] = letter_idx
    return x

def gen_submorphs(word, letter_idx, delta):
    letter = word[letter_idx]
    before = word[:letter_idx]
    after = word[letter_idx + 1:]
    before_acc = letter if SELF_LEFT else ""
    after_acc = letter if SELF_RIGHT else ""
    if KEEP_SELF:
        yield letter

    for b in reversed(before[-delta:]):
        before_acc = b + before_acc
        yield before_acc + "_"

    for a in after[:delta]:
        after_acc = after_acc + a
        yield "_" + after_acc
        # also skip 1 char
    if NOTE_WORD:
        yield word

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
        if USE_E:
            morph_tags.append("E")
        else:
            morph_tags.append("M")
    return morph_tags


def load_dataset(dataset_path, delta, universal_model=False):
    xs = []
    ys = []
    universal_model_x = []
    universal_model_y = []
    words = set()
    with open(dataset_path) as fin:
        for row in fin:
            word, target = row[:-1].split("\t")
            target = target.split(",")[0] #  multiple annotations
            words.add(word)
            x, word_dims, y = tag_word(word, target, delta)
            xs.append(x)
            ys.append(y)

    if universal_model:
        with open("/usr/share/dict/american-english") as fin:
            for row in fin:
                word = row[:-1]
                if len(word) >= UNIVERSAL_MODEL_LENGTH_MAX:
                    continue
                if len(word) == 1:
                    continue
                if "'" in word:
                    continue
                if word not in words:
                    x, word_dims, y = tag_word(word, target, delta)
                    for letter_idx, letter in enumerate(x):
                        for key in letter:
                            if key != 'position':
                                x[letter_idx][key] /= pow(len(letter), NOISE_LENGTH_COEFF) # or ,2
                    universal_model_x.append(x)
                    universal_model_y.append(y)

    universal_model_x.extend(xs)
    universal_model_y.extend(ys)
    return universal_model_x, universal_model_y

# delta = 6
# X_train, y_train = load_dataset("task1_data/training.eng.txt", delta=delta, universal_model=True)
# model = crf.CRF(
#         algorithm='ap',
#         epsilon=10**-10,
#         # max_iterations=200,
#         # algorithm='lbfgs',
#         # c1=0.1,
#         # c2=0.01,
#         all_possible_transitions=True,
#         all_possible_states=False,
#         verbose=False,
# )
# # variance=None, verbose=False)>
# 
# labels = model.classes_
# # labels.remove("START") labels.remove("STOP")
# print("[SCORING] delta", delta)
# print("load")
# X_test, y_test = load_dataset("task1_data/dev.eng.txt", delta=delta)
# print("X like:", X_test[0][3])
# print("y like:", y_test[0])
# model.fit(X_train, y_train)
# print("predict")
# y_predicted = model.predict(X_test)
# print(metrics.flat_classification_report(y_test, y_predicted, labels=labels, digits=3))
# 
# sys.exit()

report = {}
report['USE_NOISE'] = USE_NOISE
report['UNIVERSAL_MODEL_LENGTH_MAX'] = UNIVERSAL_MODEL_LENGTH_MAX
report['NOISE_LENGTH_COEFF'] = NOISE_LENGTH_COEFF
report['FEATURE_WEIGHT'] = FEATURE_WEIGHT
report['KEEP_SELF'] = KEEP_SELF
report['SELF_LEFT'] = SELF_LEFT
report['SELF_RIGHT'] = SELF_RIGHT
report['NOTE_WORD'] = NOTE_WORD
report['USE_E'] = USE_E

# for delta in DELTAS:
if True:
    delta = 15
    report['delta'] = delta
    # for exp in range(-10, -1):
    print("load", delta, NOISE_LENGTH_COEFF)
    X_train, y_train = load_dataset("task1_data/training.eng.txt", delta=delta, universal_model=USE_NOISE)
    model = crf.CRF(
            algorithm='ap',
            # epsilon=10**exp,
            # max_iterations=30,
            # algorithm='lbfgs',
            # c1=0.1,
            # c2=0.01,
            all_possible_transitions=True,
            all_possible_states=True,
            verbose=True,
    )
    model.fit(X_train, y_train)


    labels = model.classes_
    # labels.remove("START") labels.remove("STOP")
    print("[SCORING] delta", delta)
    X_test, y_test = load_dataset("task1_data/dev.eng.txt", delta=delta)
    print("X like:", X_test[0][3])
    print("y like:", y_test[0])
    y_predicted = model.predict(X_test)
    with open("/tmp/results", "a") as fout:
        print("LENS:")
        print(len(y_test), len(y_predicted))
        print(len(y_test[0]), len(y_predicted[0]))
        print(y_test[0])
        result = metrics.flat_classification_report(y_test, y_predicted, labels=labels, digits=3)
        report['result'] = result
        fout.write(json.dumps(report) + "\n")
        print(result)

def print_errors():
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
    pass
