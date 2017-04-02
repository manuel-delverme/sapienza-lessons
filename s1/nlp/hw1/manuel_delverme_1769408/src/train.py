import pickle
import random

import matplotlib.pyplot as plt
import numpy as np
import sklearn_crfsuite as crf
from nltk.corpus import words as nltk_words
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import GridSearchCV
from sklearn.learning_curve import learning_curve

DELTAS = range(2, 5, 1)
training_words = set()
SELF_LEFT = False
SELF_RIGHT = True
FEATURE_WEIGHT = 1.0

try:
    with open("cache/dictionaries.pkl", 'rb') as fin:
        existing_words, existing_stems = pickle.load(fin)
except IOError:
    existing_words = frozenset(nltk_words.words())
    existing_stems = None  # frozenset(existing_stems)
    with open("cache/dictionaries.pkl", 'wb') as fout:
        pickle.dump((existing_words, existing_stems), fout)


def parse_dataset_row(word, target, delta):
    word = "^{}$".format(word)
    morphs = ["^"]
    morphs.extend([string.split(":")[0] for string in target.split(" ") if string != ''])
    morphs.append("$")
    morphs = [morph for morph in morphs if morph != "~"]

    xs = []
    keys = []
    tags = []
    for morph in morphs:
        tags.extend(assign_labels(morph))

    for letter_idx, letter in enumerate(word):
        x = letter_to_dict(word, letter, letter_idx, delta)

        not_xs = random.sample(xs, min(len(xs), 1))
        for not_x in not_xs:
            for key in not_x.keys():
                if key not in x:
                    x[key] = 0
        keys.extend(x.keys())
        xs.append(x)

    return xs, tags, morphs


def letter_to_dict(word, letter, letter_idx, delta):
    x = {}
    for sub_morph, value in gen_features(word, letter, letter_idx, delta):
        x[sub_morph] = value
    return x


def gen_features(word, letter, letter_idx, delta):
    before = word[:letter_idx]
    after = word[letter_idx + 1:]
    before_acc = letter if SELF_LEFT else ""
    after_acc = letter if SELF_RIGHT else ""

    yield '_bias_', FEATURE_WEIGHT

    for b in reversed(before[-delta - 1:]):
        before_acc = b + before_acc
        yield before_acc + "_", FEATURE_WEIGHT  # * (1 / len(before_acc))

    for a in after[:delta]:
        after_acc = after_acc + a
        yield "_" + after_acc, FEATURE_WEIGHT  # * (1 / len(after_acc))

    preceding_word = letter
    for letter in reversed(word[:letter_idx]):
        preceding_word = letter + preceding_word
        if preceding_word in existing_words:
            yield '_right_of_real_word_', FEATURE_WEIGHT
            break

    if word[letter_idx:] in existing_words:
        yield '_left_of_real_word_', FEATURE_WEIGHT

    idx_from_end = len(word) - letter_idx + 1
    if 0 < letter_idx < 3:
        yield '_idx_from_beginning_{}_'.format(letter_idx), FEATURE_WEIGHT
    elif 0 < idx_from_end < 3:
        yield '_idx_to_end_{}_'.format(idx_from_end), FEATURE_WEIGHT


def assign_labels(morph):
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
        morph_tags.append("E")
    return morph_tags


def load_dataset(dataset_paths, delta):
    cache_file_name = "cache/{0}{1}.pkl".format('.'.join(dataset_paths).replace("/", ""), str(delta))
    try:
        with open(cache_file_name, 'rb') as cache_file:
            xs, ys, training_morphemes = pickle.load(cache_file)
    except IOError:
        xsi = []
        ysi = []
        xs = []
        ys = []
        training_morphemes = []
        words = []

        for dataset_path in dataset_paths:
            with open(dataset_path) as fin:
                for row in fin:
                    if "crowd" in dataset_path:
                        tokens = row[:-1].split("\t")
                        word = tokens.pop(0)
                        target = " ".join([t + ":TRASH" for t in tokens])
                    else:
                        word, target = row[:-1].split("\t")
                        target = target.split(",")[0]  # multiple annotations
                    x, y, morphs = parse_dataset_row(word, target, delta)
                    words.append(word)
                    training_morphemes.extend(morphs)
                    xs.append(x)
                    ys.append(y)

        xs.extend(xsi)
        ys.extend(ysi)
        training_words.update(words)
        training_morphemes = set(morph for morph in training_morphemes if len(morph) > 2)
        with open(cache_file_name, 'wb') as cache_fout:
            pickle.dump((xs, ys, training_morphemes), cache_fout)
            print("saved to ", cache_file_name)
    return xs, ys, training_morphemes


def get_sub_morphemes(word, training_morphemes):
    # yields a list of morphemes
    if len(word) == 0:
        yield []

    for morpheme in training_morphemes:
        if word.find(morpheme) == 0:
            subword = word[len(morpheme):]
            for submorphemes in get_sub_morphemes(subword, training_morphemes):
                yield [word] + submorphemes


def generate_synthetic_data(training_morphemes, training_words, delta):
    cache_file_name = "cache/" + str(delta) + "_synth.pkl"
    try:
        with open(cache_file_name, 'rb') as fin:
            synth_xs, synth_ys = pickle.load(fin)
    except IOError:
        print("generating morphemes from #training_morpehemes", training_morphemes)
        synth_xs = []
        synth_ys = []
        nr_words = len(existing_words)
        for idx, word in enumerate(existing_words):
            if word in training_words:
                continue
            if idx % 1000 == 0:
                print((idx / nr_words))
            for morphemes in get_sub_morphemes(word, training_morphemes):
                word = ''.join(morphemes)
                target = ' '.join(morpheme + ":TRASH" for morpheme in morphemes)
                x, y, _ = parse_dataset_row(word, target, delta)

                for letter_idx, letter in enumerate(x):
                    x[letter_idx]['is_synth'] = 1
                    # x["_" + word + "_"] = 1
                    # x['_support_'] = 1
                    x[letter_idx]['morpheme_count_' + str(len(morphemes))] = 1
                synth_xs.append(x)
                synth_ys.append(y)
        print("generated {} samples".format(len(synth_ys)))

        with open(cache_file_name, 'wb') as fout:
            pickle.dump((synth_xs, synth_ys), fout)
    return synth_xs, synth_ys


def clean_data(model, X_synth, y_synth):
    clean_xs = []
    clean_ys = []

    for word, tags in zip(X_synth, y_synth):
        marginals = model.predict_marginals_single(word)
        score = 0
        for idx, tag in enumerate(tags):
            score += marginals[idx][tag]
        if score / len(tags) < 0.8:
            clean_xs.append(word)
            clean_ys.append(tags)
        else:
            pass
    print("dropped", len(y_synth) - len(clean_ys))
    return clean_xs, clean_ys


def score_all(model, X_test, y_test):
    y_predicted = model.predict(X_test)
    assert len(X_test) > 0
    assert len(y_test) > 0
    assert len(y_predicted) > 0
    D = 0
    H = 0
    I = 0

    boundaries = ["E", "S"]

    for sample_idx, (word, yps, yts) in enumerate(zip(X_test, y_predicted, y_test)):
        predicted_boundaries = {idx for idx, yp in enumerate(yps) if yp in boundaries}
        test_boundaries = {idx for idx, yt in enumerate(yts) if yt in boundaries}

        bad_boundaries = predicted_boundaries - test_boundaries
        misseD_boundaries = test_boundaries - predicted_boundaries
        D += len(misseD_boundaries)
        Hits = predicted_boundaries.intersection(test_boundaries)
        H += len(Hits)
        I += len(bad_boundaries)
    precision = H / (H + I)
    recall = H / (H + D)
    f1_score = 2 * (precision * recall) / (precision + recall)
    # print("f1_score", f1_score)
    return f1_score, precision, recall


def score_f1(model, X, y):
    return score_all(model, X, y)[0]


def score_prec(model, X, y):
    return score_all(model, X, y)[1]


def score_recall(model, X, y):
    return score_all(model, X, y)[2]


def main():
    training_datasets = [
        "task1_data/training.eng.txt",
        "task1_data/dev.eng.txt",
        "task1_data/crowd-sourced-annotations.txt",
    ]
    best_param, scores = find_best_parameters(training_datasets)

    print("using", best_param, "to train")
    best_delta, best_crf_params = best_param

    X_all, y_all, _ = load_dataset(training_datasets + ["task1_data/test.eng.txt"], delta=best_delta)
    X_test, y_test, _ = load_dataset(["task1_data/test.eng.txt"], delta=best_delta)
    X_train, y_train, _ = load_dataset(training_datasets, delta=best_delta)

    print("training original model")
    original_model = crf.CRF(**best_crf_params)
    original_model.fit(X_train, y_train)

    plt.title("learning curve")
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(original_model, X_all, y_all, cv=3, n_jobs=-1,
                                                            train_sizes=np.logspace(-2, 0, 10), verbose=True, )
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std, train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std, test_scores_mean + test_scores_std, alpha=0.1,
                     color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")

    plt.legend(loc="best")

    f1_score = cross_val_score(original_model, X_all, y_all, scoring=score_f1, cv=3, n_jobs=-1)
    original_f1 = sum(f1_score) / len(f1_score)
    recall_score = cross_val_score(original_model, X_all, y_all, scoring=score_recall, cv=3, n_jobs=-1)
    original_recall = sum(recall_score) / len(recall_score)
    prec_score = cross_val_score(original_model, X_all, y_all, scoring=score_prec, cv=3, n_jobs=-1)
    original_prec = sum(prec_score) / len(prec_score)

    print("original score\t", original_f1, original_prec, original_recall)

    original_score2 = score_f1(original_model, X_test, y_test)
    print("original score2\t", original_score2)

    plt.show()
    return original_model


def find_best_parameters(training_datasets):
    best_delta_score = 0
    grid_search_space = {
        'algorithm': ['ap'],
        'epsilon': np.logspace(-4, -2, 4),
        'max_iterations': np.linspace(10, 100, 4),
        'all_possible_transitions': [False, True],
    }
    scores = {}

    for delta in DELTAS:
        X, y, training_morphemes = load_dataset(training_datasets, delta=delta)
        model = crf.CRF()
        print("fitting delta:", delta)

        grid_search = GridSearchCV(estimator=model, cv=3, param_grid=grid_search_space, n_jobs=-1).fit(X, y)

        scores[delta] = grid_search.grid_scores_
        print("Best parameters set found on development set:")
        print(grid_search.best_params_)

        model = crf.CRF(**grid_search.best_params_)
        xval_scores = cross_val_score(model, X, y, cv=5, scoring=score_f1)
        delta_score = sum(xval_scores) / len(xval_scores)
        print("scores:", xval_scores, "avg", delta_score)
        if delta_score > best_delta_score:
            print("^^^^ new best parameters ^^^^")
            best_delta_score = delta_score  # best_weight_score
            best_param = (delta, grid_search.best_params_)  # best_weight)

    return best_param, scores


if __name__ == "__main__":
    try:
        raise IOError
        with open("model/model.pkl", 'rb') as fin:
            model = pickle.load(fin)
    except IOError:
        model = main()
        with open("model/model.pkl", 'wb') as fout:
            print("saved to ", "model/model.pkl")
            pickle.dump(model, fout)
    print("output synth from load_data instead of stupid flags!")
    print("negative sampling [slides]")
    print("READ https://en.wikipedia.org/wiki/Morpheme")
