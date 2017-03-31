import sklearn_crfsuite as crf
import random
import numpy as np
from nltk.corpus import words as nltk_words
from sklearn.model_selection import train_test_split
from sklearn.cross_validation import ShuffleSplit
from sklearn.grid_search import GridSearchCV
from sklearn.learning_curve import learning_curve
from sklearn.cross_validation import cross_val_score


# DELTAS = range(3, 10)
DELTAS = range(4, 10)
UNIVERSAL_MODEL_LENGTH_MAX = 4
NOISE_LENGTH_COEFF = 0
USE_SYNTETIC_DATA = True
FEATURE_WEIGHT = 1.0
KEEP_SELF = True
SELF_LEFT = False
SELF_RIGHT = True
NOTE_WORD = False
USE_E = True
USE_B = True
USE_S = True
existing_words = set(nltk_words.words())
existing_almost_words = set((nltk.stem(word) for word in existing_words))
try:
    existing_almost_words.remove("")
except KeyError:
    pass
existing_words = frozenset(existing_words)
existing_almost_words = frozenset(existing_almost_words)

IS_SYNTH = False

def parse_dataset_row(word, target, delta, support=False):
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
        letter_tag = tags[letter_idx]
        x = letter_to_dict(word, letter, letter_idx, delta, support)

        if support:
            x[word] = 1

        not_xs = random.sample(xs, min(len(xs), 1))
        for not_x in not_xs:
            for key in not_x.keys():
                if key not in x:
                    x[key] = 0
        # try:
        #     x['next_' + tags[letter_idx + 1]] = 1
        # except IndexError:
        #     pass
        # try:
        #     x['prev_' + tags[letter_idx - 1]] = 1
        # except IndexError:
        #     pass
        keys.extend(x.keys())
        xs.append(x)

    # if len(xs) != len(tags):
    #     good_tags = [tag for tag in tags if tag != "~"]
    #     good_tags = good_tags[0:len(xs) - 1] + [good_tags[-1]]
    #     tags = good_tags

    # for idx, x in enumerate(xs):
    #     for key in keys:
    #         if key not in x:
    #             xs[idx][key] = 0
    return xs, tags


def letter_to_dict(word, letter, letter_idx, delta, support):
    x = {}
    for sub_morph, value in gen_features(word, letter, letter_idx, delta, support):
        x[sub_morph] = value
    return x


def gen_features(word, letter, letter_idx, delta, support):
    before = word[:letter_idx]
    after = word[letter_idx + 1:]
    before_acc = letter if SELF_LEFT else ""
    after_acc = letter if SELF_RIGHT else ""

    yield 'bias', FEATURE_WEIGHT

    # if support:
    #     yield word

    if KEEP_SELF:
        yield letter, FEATURE_WEIGHT

    #TODO: yield left[1] 2 or 3 time
    #TODO: position of morpheme in word, beginning middle end

    for b in reversed(before[-delta:]):
        before_acc = b + before_acc
        # yield before_acc + "_", FEATURE_WEIGHT * (1/len(before_acc))
        yield before_acc + "_", 1

    for a in after[:delta]:
        after_acc = after_acc + a
        # yield "_" + after_acc, FEATURE_WEIGHT * (1/len(after_acc))
        yield "_" + after_acc, 1

    if not IS_SYNTH:
        word = word[1:-1]

        if NOTE_WORD:
            yield word, FEATURE_WEIGHT

        # if word[:letter_idx-1] in existing_almost_words:
        #     # print("right", word[:letter_idx])
        #     yield 'right_of_almost_word'

        # if word[letter_idx:-1] in existing_almost_words:
        #     # print("left", word[letter_idx:])
        #     yield 'left_of_almost_word'

        # if word[:-1] in existing_almost_words:
        #     yield 'almost_word'

        preceding_word = letter
        for letter in reversed(word[:letter_idx]):
            preceding_word = letter + preceding_word
            if preceding_word in existing_words:
                # print("right", word[:letter_idx])
                yield 'right_of_real_word', FEATURE_WEIGHT
                break

        if word[letter_idx:] in existing_words:
            # print("left", word[letter_idx:])
            yield 'left_of_real_word', FEATURE_WEIGHT

        if word in existing_words:
            yield 'real_word', FEATURE_WEIGHT

    # x['length:' + str(len(word))] = 1
    yield '_idx_from_beginning_{}'.format(letter_idx), FEATURE_WEIGHT

    idx_from_end = len(word) - letter_idx + 1
    yield '_idx_to_end_{}'.format(idx_from_end), FEATURE_WEIGHT

    # yield '_rel_idx_from_beginning_{}'.format(int((letter_idx  * 10) / len(word)))
    # yield '_rel_idx_to_end_{}'.format(int((10 * idx_from_end) / len(word)))


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
        if USE_E:
            morph_tags.append("E")
        else:
            morph_tags.append("M")
    return morph_tags



def load_dataset(dataset_paths, delta, synthetic_data=False, support=False):
    xsi = []
    ysi = []
    words = set()
    morphs = set()
    xs = []
    ys = []
    training_words = []
    IS_SYNTH = synthetic_data
    if not synthetic_data:
        for dataset_path in dataset_paths:
            with open(dataset_path) as fin:
                for row in fin:
                    if "crowd" in dataset_path:
                        tokens = row[:-1].split("\t")
                        word = tokens.pop(0)
                        target = " ".join([ t + ":TRASH" for t in tokens])
                    else:
                        word, target = row[:-1].split("\t")
                        target = target.split(",")[0]  # multiple annotations
                    x, y = parse_dataset_row(word, target, delta, support=support)
                    training_words.append(word)
                    xs.append(x)
                    ys.append(y)

        xs.extend(xsi)
        ys.extend(ysi)
        training_words.update(words)
        training_morphemes.update(morphs)
    training_words = frozenset(training_words)

    if synthetic_data:
        try:
            with open("cache/" + dataset_path + "_synth.pkl", 'rb') as fin:
                synth_xs, synth_ys = pickle.load(fin)
        except IOError:
            for radius in range(2, 5):
                print("generating len:{} synthetic data".format(radius))
                for candidate_morphemes in itertools.combinations(training_morphemes, radius):
                    word = ''.join(candidate_morphemes)
                    if word in training_words or word not in existing_words:
                        continue

                    x, y, _ = parse_dataset_row(word, word + ":TRASH ", delta)
                    for letter_idx, letter in enumerate(x):
                        x[letter_idx]['is_synth'] = 1
                        x[letter_idx]['morpheme_count_' + str(radius)] = 1
                    synth_xs.append(x)
                    synth_ys.append(y)
                print("generated {} samples".format(len(synth_ys)))
            with open("cache/" + dataset_path + "_synth.pkl", 'wb') as fout:
                pickle.dump((synth_xs, synth_ys), fout)
    return xs, ys, synth_xs, synth_ys


def score_model(X_test, y_test, y_predicted):
    assert len(X_test) > 0
    assert len(y_test) > 0
    assert len(y_predicted) > 0
    D = 0
    H = 0
    I = 0

    if USE_E:
        boundaries = ["E"]
    elif USE_B:
        boundaries = ["B"]
    else:
        raise Exception("WTF?")
    if USE_S:
        boundaries.append("S")

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
    return f1_score

def tandem_predict(model, synth_model, X, weight):
    y_predicted = []
    for word in X:
        word_tags_predicted = []

        ys = model.predict_marginals_single(word)
        ys_synth = synth_model.predict_marginals_single(word)

        for idx, y_synth in enumerate(ys_synth):
            best_key = ''
            best_val = 0
            for key in y_synth.keys():
                key_val = ys[idx][key] + weight * y_synth[key]
                # key_val = max(ys[idx][key], weight * y_synth[key])

                # key_val = ys[idx][key] + np.exp(np.log(weight * y_synth[key]))
                # key_val = ys[idx][key]
                if key_val > best_val:
                    best_val = key_val
                    best_key = key
            word_tags_predicted.append(best_key)
        y_predicted.append(word_tags_predicted)
    return y_predicted


def clean_data(model, X_synth, y_synth):
    clean_xs = []
    clean_ys = []

    for word, tags in zip(X_synth, y_synth):
        marginals = model.predict_marginals_single(word)
        score = 0
        for idx, tag in enumerate(tags):
            score += marginals[idx][tag]
        if score/len(tags) < 0.8:
            clean_xs.append(word)
            clean_ys.append(tags)
        else:
            pass
    print("dropped", len(y_synth) - len(clean_ys))
    return clean_xs, clean_ys



def main():
    report = {
        'USE_SYNTETIC_DATA': USE_SYNTETIC_DATA,
        'UNIVERSAL_MODEL_LENGTH_MAX': UNIVERSAL_MODEL_LENGTH_MAX,
        'NOISE_LENGTH_COEFF': NOISE_LENGTH_COEFF,
        'FEATURE_WEIGHT': FEATURE_WEIGHT,
        'KEEP_SELF': KEEP_SELF,
        'SELF_LEFT': SELF_LEFT,
        'SELF_RIGHT': SELF_RIGHT,
        'NOTE_WORD': NOTE_WORD,
        'USE_E': USE_E
    }

    best_delta_score = 0
    best_delta = -1

    crf_params = {
        'algorithm':'ap',
        'epsilon':10 ** -4,
        'max_iterations':100,
        'all_possible_transitions':True,
        # all_possible_states=True,
        'verbose':False,
    }
    crf_synth_params = {
        'algorithm': 'ap',
        'epsilon': 10 ** -4,
        'max_iterations': 100,
        'verbose': False,
    }

    X_train, y_train, _, _ = load_dataset(["task1_data/training.eng.txt"], delta=6)
    model = crf.CRF(**crf_params)
    model.fit(X_train, y_train)

    done = set()
    for row in open("annotation.csv"):
        word = row[:-1].split(",")[0]
        done.add(word)

    for word in existing_words:
        if word in done:
            continue
        xsi = []
        for letter_idx, letter in enumerate(word):
            x = letter_to_dict(word, letter, letter_idx, 6)
            xsi.append(x)
        word_tags = model.predict_single(xsi)
        print(word, end="\t", flush=True)
        for letter, word_tag in zip(word, word_tags):
            print(letter, end='')
            if word_tag == 'B' or word_tag == 'S':
                print("\t", end='')
        print()

    for delta in DELTAS:

        X, y = load_dataset(["task1_data/training.eng.txt",
                             "task1_data/crowd-sourced-annotations.txt",
                             "task1_data/dev.eng.txt"
                            ], delta=delta, synthetic_data=False)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        cv = ShuffleSplit(len(X_train), n_iter=10, test_size=0.2, random_state=42)
        model = crf.CRF(**crf_params)

        # weights = np.logspace(-6, -1, 10)

        epsilon_space = np.logspace(-10, -1, 20)
        weights_space = np.linspace(0, 2, 10)
        weights_space = np.linspace(100, 1000, 10)

        import ipdb; ipdb.set_trace()
        classifier = GridSearchCV(estimator=model, cv=cv, param_grid=dict(epsilon=epsilon_space, max_iterations=max_iterations_space))

        classifier.fit(X_train, y_train)

        title = "Learning Curves (Averaged, AP, $\delta={})".format(delta)
        # http://scikit-learn.org/stable/modules/learning_curve.html
        # http://scikit-learn.org/stable/auto_examples/model_selection/plot_learning_curve.html
        # http://scikit-learn.org/stable/modules/learning_curve.html
        plot_learning_curve(model, title, X_train, y_train, cv=cv)
        plt.show()

        # http://scikit-learn.org/stable/modules/cross_validation.html
        cross_val_score(model, X, y)

        print("fitting {} datapoint on model".format(len(X_train)), end='...')
        model.fit(X_train, y_train)

        # X_train, y_train = load_dataset([], delta=delta, synthetic_data=True)
        X_train, y_train = load_dataset(["task1_data/training.eng.txt",
                                         "task1_data/crowd-sourced-annotations.txt"
                                        ], delta=delta, synthetic_data=False, support=True)
        synt_model = crf.CRF(**crf_params)
        # print("fitting {} datapoint on synth".format(len(X_train)), end='...')
        synt_model.fit(X_train, y_train)

        # print("Xtrain like:", X_train[0][3])
        # print("Xnoise like:", X_train[-1][3])
        # print("overfit?", model.score(X_train, y_train))

        print("[SCORING] delta", delta, end='...')
        X_test, y_test, = load_dataset(["task1_data/dev.eng.txt", ], delta=delta)
        # print("y like:", y_test[0])
        y_predicted = model.predict(X_test)
        original_score = score_model(X_test, y_test, y_predicted)
        print()
        print("original score:", original_score)

        best_weight_score = original_score
        best_weight = 0
        for weight in (w/100 for w in range(20, 200, 2)):
            y_predicted = tandem_predict(model, synt_model, X_test, weight=weight)
            weight_score = score_model(X_test, y_test, y_predicted)
            print("weight", weight, weight_score)
            if weight_score > best_weight_score:
                best_weight_score = weight_score
                best_weight = weight

        print("best weight for delta={} is {} with score: {}".format(delta, best_weight, best_weight_score))
        print("improvement over original: {}".format(best_weight_score - original_score))
        if best_weight_score > best_delta_score:
            print("^^^^ new best parameters ^^^^")
            best_delta_score = best_weight_score
            best_param = (delta, best_weight)


    # final training
    print("using", best_param, "to train")
    delta, weight = best_param
    X_train, y_train = load_dataset(["task1_data/training.eng.txt",
                                     "task1_data/dev.eng.txt",
                                     "task1_data/crowd-sourced-annotations.txt",
                                    ], delta=best_delta, synthetic_data=False)

    print("fitting {} datapoint on model".format(len(X_train)))
    model = crf.CRF(**crf_params)
    model.fit(X_train, y_train)

    # X_train, y_train = load_dataset([], delta=delta, synthetic_data=True)
    X_train, y_train = load_dataset(["task1_data/training.eng.txt",
                                     "task1_data/dev.eng.txt",
                                     "task1_data/crowd-sourced-annotations.txt"
                                    ], delta=delta, synthetic_data=False, support=True)
    synt_model = crf.CRF(**crf_params)
    synt_model.fit(X_train, y_train)

    # print("[SCORING] delta", delta, end='...')
    X_test, y_test, = load_dataset(["task1_data/test.eng.txt"], delta=delta)
    # print("y like:", y_test[0])
    y_predicted = model.predict(X_test)
    original_score = score_model(X_test, y_test, y_predicted)
    print("original score\t", original_score)

    y_predicted = tandem_predict(model, synt_model, X_test, weight=weight)
    voting_score = score_model(X_test, y_test, y_predicted)
    print("voting   score\t", voting_score)
    print("improvement:", voting_score - original_score)
    return model


if __name__ == "__main__":
    model = main()
    print("output synth from load_data instead of stupid flags!")
    print("negative sampling [slides]")
    print("READ https://en.wikipedia.org/wiki/Morpheme")
