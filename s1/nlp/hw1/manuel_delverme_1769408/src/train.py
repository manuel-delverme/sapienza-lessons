import sklearn_crfsuite as crf
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


def tag_word(target, delta=1):
    data = set()
    morphs_and_data = target.split(" ")
    for morph_and_data in morphs_and_data:
        morph, _ = morph_and_data.split(":")

        if len(morph) == 1:
            morph_tags = "S"
        else:
            morph_tags = "B"
            for _ in morph[1:-1]:
                morph_tags += "M"
            morph_tags += "E"

        for letter_idx, letter in enumerate(morph):
            # print("letter:", letter)
            before = morph[:letter_idx]
            after = reversed(morph[letter_idx + 1:])
            before_acc = letter
            after_acc = letter
            # print(letter, morph_tags[letter_idx])
            data.add((letter, morph_tags[letter_idx]))

            for b, a in itertools.zip_longest(before, after, fillvalue=""):
                if len(before_acc) > delta or len(after_acc) > delta:
                    break

                before_acc = b + before_acc
                after_acc = after_acc + a
                # print(before_acc, morph_tags[letter_idx])
                # print(after_acc, morph_tags[letter_idx])
                data.add((before_acc, morph_tags[letter_idx]))
                data.add((after_acc, morph_tags[letter_idx]))
    tags = []
    morphs = []
    data.add(("$", "STOP"))
    data.add(("^", "START"))
    for sub_morph, tag in data:
        # print(sub_morph, tag)
        morphs.append(sub_morph)
        tags.append(tag)
    return morphs, tags

def load_dataset(delta = 1):
    xs = []
    ys = []
    with open("task1_data/training.eng.txt") as fin:
        for row in fin:
            _, target = row.split("\t")
            x, y = tag_word(target, delta=1)
            # print(x, target, y)
            xs.append(x)
            ys.append(y)
    return xs, ys

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


def main():
    x, y = load_dataset()
    # X_train = [sent2features(s) for s in train_sents]
    # y_train = [sent2labels(s) for s in train_sents]

    # X_test = [sent2features(s) for s in test_sents]
    # y_test = [sent2labels(s) for s in test_sents]
    model = crf.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=100,
            all_possible_transitions=True
    )
    model.fit(x, y)
    # with open("model.pkl", "wb") as fout:
    #     pickle.dump(model, fout)



# if __name__ == "__main__":
#     main()

x, y = load_dataset(delta = 1)
# X_train = [sent2features(s) for s in train_sents]
# y_train = [sent2labels(s) for s in train_sents]

# X_test = [sent2features(s) for s in test_sents]
# y_test = [sent2labels(s) for s in test_sents]
model = crf.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
)
model.fit(x, y)
print("predict cake")
print(model.predict("^cake$"))
