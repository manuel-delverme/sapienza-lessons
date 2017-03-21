import sklearn_crfsuite as crf
import random
# from nltk.corpus import cmudict
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
import sklearn.metrics
# from sklearn.cross_validation import cross_val_score
# from sklearn.grid_search import RandomizedSearchCV

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
import json

# d = cmudict.dict()
DELTAS = range(4, 5)
UNIVERSAL_MODEL_LENGTH_MAX = 4
NOISE_LENGTH_COEFF = 0
USE_NOISE = False
FEATURE_WEIGHT = 1.0
KEEP_SELF = True
SELF_LEFT = False
SELF_RIGHT = True
NOTE_WORD = False
USE_E = True
USE_B = True
USE_S = True
existing_words = set()
with open("google-10000-english.txt") as fin:
    for row in fin:
        if len(row) > 2:
            existing_words.add(row[:-1])

def tag_word(word, target, delta):
    word = "^{}$".format(word)
    morphs = ["^"]
    morphs.extend([string.split(":")[0] for string in target.split(" ")])
    poss = [string.split(":")[1] for string in target.split(" ")]
    morphs.append("$")

    dimensions = set()
    xs = []
    ys = []
    tags = []
    for morph in morphs:
        tags.extend(tag_morph(morph))

    for letter_idx, letter in enumerate(word):
        # import ipdb; ipdb.set_trace()
        # if len(poss) > 0:
        #     pos = poss[letter_idx]
        # else:
        #     pos = None
        pos = None
        x = letter_to_dict(word, morph, letter, letter_idx, delta, pos)
        # try:
        #     x['next_' + tags[letter_idx + 1]] = 1
        # except IndexError:
        #     pass
        # try:
        #     x['prev_' + tags[letter_idx - 1]] = 1
        # except IndexError:
        #     pass
        dimensions.update(x.keys())
        xs.append(x)

    if len(xs) != len(tags):
        good_tags = [tag for tag in tags if tag != "~"]
        good_tags = good_tags[0:len(xs)-1] + [good_tags[-1]]
        tags = good_tags
    return xs, dimensions, tags

def letter_to_dict(word, morph, letter, letter_idx, delta, pos):
    x = {}
    if pos is not None:
        x[pos] = 1

    for sub_morph in gen_submorphs(word, letter_idx, delta):
        x[sub_morph] = FEATURE_WEIGHT

    word = word[1:-1]

    if word[:letter_idx] in existing_words:
        # print("right", word[:letter_idx])
        x['right_of_real_word'] = 1

    if word[letter_idx:] in existing_words:
        # print("left", word[letter_idx:])
        x['left_of_real_word'] = 1

    if word in existing_words:
        x['real_word'] = 1
    else:
        x['real_word'] = 0

    # def syl(word):
    #     return [list(y for y in x if y[-1].isdigit()) for x in d[word.lower()]]

    # try:
    #     for syls in syl(word[1:-1]):
    #         for syl in syls:
    #             x[syl] = 1
    # except KeyError as e:
    #     pass
    #     # print("skipping syl", e)
    # x['length:' + str(len(word))] = 1
    x['_lidx_{}'.format(letter_idx)] = 1
    x['_ridx_{}'.format(len(word) - letter_idx)] = 1
    x['bias'] = 1
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

    letter = word[letter_idx: letter_idx + 2]
    before = word[:letter_idx]
    after = word[letter_idx + 2:]
    before_acc = letter if SELF_LEFT else ""
    after_acc = letter if SELF_RIGHT else ""
    if KEEP_SELF:
        yield letter

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
    words = []
    with open(dataset_path) as fin:
        for row in fin:
            word, target = row[:-1].split("\t")
            target = target.split(",")[0] #  multiple annotations
            words.append(word)
            x, word_dims, y = tag_word(word, target, delta)
            xs.append(x)
            ys.append(y)

    if universal_model:
        print("ADDING NOISE")
        with open("clean_morphemes.csv") as fin:
            for row in fin:
                word = row[:-1]
                # if len(word) >= universal_model_length_max:
                #     continue
                # if len(word) == 1:
                #     continue
                # if "'" in word:
                #     continue
                if word not in words:
                    x, word_dims, y = tag_word(word, None, delta)
                    for letter_idx, letter in enumerate(x):
                        del x[letter_idx]['bias']
                        x[letter_idx]['is_noise'] = 1
                        x[letter_idx]['noise_length' + str(len(word))] = 1
                    universal_model_x.append(x)
                    universal_model_y.append(y)
    # universal_model_x.extend(xs)
    # universal_model_y.extend(ys)
    return xs, ys, universal_model_x, universal_model_y, words

def score_model(X_test, texts, y_test, y_predicted):
    bad_boundaries = 0
    D = 0
    H = 0
    I = 0

    # with open("/tmp/results", "a") as fout:
    #     fout.write(json.dumps(report) + "\n")
    if USE_E:
        boundaries = ["E"]
    elif USE_B:
        boundaries = ["B"]
    else:
        raise Exception("WTF?")
    if USE_S:
        boundaries.append("S")

    for sample_idx, (word, word_text, yps, yts) in enumerate(zip(X_test, texts, y_predicted, y_test)):
        # if word_text == 'bountiful':
        #     import ipdb; ipdb.set_trace()
        #     print(word_text)

        predicted_boundaries = {idx for idx, yp in enumerate(yps) if yp in boundaries}
        test_boundaries      = {idx for idx, yt in enumerate(yts) if yt in boundaries}

        # print("predicted_boundaries", predicted_boundaries)
        # print("test_boundaries", test_boundaries)
        bad_boundaries = predicted_boundaries - test_boundaries
        # print("bad_bound", bad_boundaries)

        misseD_boundaries = test_boundaries - predicted_boundaries
        D += len(misseD_boundaries)
        # print("missed", misseD_boundaries)

        Hits = predicted_boundaries.intersection(test_boundaries)
        H += len(Hits)
        # print("hits", Hits)

        I += len(bad_boundaries)
        # print("incorrects", bad_boundaries)

        precision = H / (H + I)
        recall = H / (H + D)
        f1_score = 2 * (precision * recall) / (precision + recall)

        # print("precision", precision)
        # print("recall", recall)
        # print("hits", H)
        # print("I", I)
        # print("D", D)
        # print("f1", f1_score)
        # result = metrics.flat_f1_score(y_test[:sample_idx + 1], y_predicted[:sample_idx + 1], labels=boundaries, average='weighted')
        # print('sklearn F1 RESULT:', result)
        # print('F1 ERROR', result - f1_score)

        if predicted_boundaries != test_boundaries:
            # print("missclassification:", end='')
            # for y, letter in zip(yps, word_text):
            #     print(letter, end='')
            # print()

            # print("guessed:")
            # for y, letter in zip(yps, word_text):
            #     if y in boundaries: print("\t", end='')
            #     print(letter, end='')

            # print("\nwas:")
            # for y, letter in zip(yts, word_text):
            #     if y in boundaries: print("\t", end='')
            #     print(letter, end='')

            # print("\ni predicted")
            # for y in yps: print(y, end='\t')

            # print("\ntest said:")
            # for y in yts: print(y, end='\t')
            # print("")
            pass

    # result = metrics.flat_f1_score(y_test, y_predicted, labels=boundaries, average='weighted')
    # print('sklearn F1 RESULT:', result)

    # result = sklearn.metrics.recall_score(y_test, y_predicted, labels=boundaries, average='weighted')
    # print('sklearn recall RESULT:', result)

    precision = H / (H + I)
    recall = H / (H + D)
    f1_score = 2 * (precision * recall) / (precision + recall)
    report['result'] = f1_score

    # print("precision", precision)
    # print("recall", recall)
    print("f1_score", f1_score)

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

for delta in DELTAS:
    report['delta'] = delta
    X_train, y_train, X_noise, y_noise, words = load_dataset("task1_data/training.eng.txt", delta=delta, universal_model=USE_NOISE)
    model = crf.CRF(
            algorithm='ap',
            epsilon=10**-2,
            max_iterations=1000,
            # algorithm='lbfgs',
            # c1=0.1,
            # c2=0.01,
            # all_possible_transitions=False,
            # all_possible_states=False,
            verbose=True,
    )
    if USE_NOISE:
        X_train.extend(X_noise)
        y_train.extend(y_noise)
    print("fitting {} datapoint".format(len(X_train)))
    model.fit(X_train, y_train)
    print("Xtrain like:", X_train[0][3])
    print("Xnoise like:", X_train[-1][3])
    print("overfit?", model.score(X_train, y_train))

    labels = model.classes_
    # labels.remove("START") labels.remove("STOP")
    print("[SCORING] delta", delta)
    X_test, y_test, _, _, words = load_dataset("task1_data/dev.eng.txt", delta=delta)
    # print("y like:", y_test[0])
    y_predicted = model.predict(X_test)
    score_model(X_test, words, y_test, y_predicted)

print("READ https://en.wikipedia.org/wiki/Morpheme")
