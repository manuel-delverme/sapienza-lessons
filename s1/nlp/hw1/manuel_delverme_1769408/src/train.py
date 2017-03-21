import sklearn_crfsuite as crf
from nltk.corpus import words as nltk_words

DELTAS = range(4, 5)
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


def parse_dataset_row(word, target, delta):
    word = "^{}$".format(word)
    morphs = ["^"]
    morphs.extend([string.split(":")[0] for string in target.split(" ") if string != ''])
    morphs.append("$")
    morphs = [morph for morph in morphs if morph != "~"]

    xs = []
    tags = []
    for morph in morphs:
        tags.extend(assign_labels(morph))

    for letter_idx, letter in enumerate(word):
        letter_tag = tags[letter_idx]
        x = letter_to_dict(word, letter, letter_idx, delta)
        # try:
        #     x['next_' + tags[letter_idx + 1]] = 1
        # except IndexError:
        #     pass
        # try:
        #     x['prev_' + tags[letter_idx - 1]] = 1
        # except IndexError:
        #     pass
        xs.append(x)

    # if len(xs) != len(tags):
    #     good_tags = [tag for tag in tags if tag != "~"]
    #     good_tags = good_tags[0:len(xs) - 1] + [good_tags[-1]]
    #     tags = good_tags
    return xs, tags


def letter_to_dict(word, letter, letter_idx, delta):
    x = {}
    for sub_morph in gen_features(word, letter, letter_idx, delta):
        x[sub_morph] = FEATURE_WEIGHT
    return x


def gen_features(word, letter, letter_idx, delta):
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

    word = word[1:-1]

    if NOTE_WORD:
        yield word

    if word[:letter_idx] in existing_words:
        # print("right", word[:letter_idx])
        yield 'right_of_real_word'

    if word[letter_idx:] in existing_words:
        # print("left", word[letter_idx:])
        yield 'left_of_real_word'

    if word in existing_words:
        yield 'real_word'

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
    yield '_idx_from_beginning_{}'.format(letter_idx)
    yield '_idx_to_end_{}'.format(len(word) - letter_idx)
    yield 'bias'


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


def load_dataset(dataset_path, delta, synthetic_data=False):
    xs = []
    ys = []
    training_words = []
    with open(dataset_path) as fin:
        for row in fin:
            word, target = row[:-1].split("\t")
            target = target.split(",")[0]  # multiple annotations
            training_words.append(word)
            x, y = parse_dataset_row(word, target, delta)
            xs.append(x)
            ys.append(y)

    training_words = frozenset(training_words)
    if synthetic_data:
        print("ADDING NOISE")
        with open("clean_morphemes.csv") as fin:
            for row in fin:
                word = row[:-1]
                if word in training_words:
                    continue
                x, y = parse_dataset_row(word, word + ":TRASH ", delta)
                for letter_idx, letter in enumerate(x):
                    # del x[letter_idx]['bias']
                    x[letter_idx]['is_noise'] = 1
                    x[letter_idx]['noise_length' + str(len(word))] = 1
                xs.append(x)
                ys.append(y)
        with open("madeupdata2") as fin:
            for row in fin:
                word, target = row[:-1].split("\t")
                if word in training_words:
                    continue

                x, y = parse_dataset_row(word, target, delta)
                for letter_idx, letter in enumerate(x):
                    x[letter_idx]['is_made_up_2'] = 1
                    x[letter_idx]['noise_length' + str(len(word))] = 1
                xs.append(x)
                ys.append(y)
        # with open("madeupdata3") as fin:
        #     for row in fin:
        #         word, target = row[:-1].split("\t")
        #         if word in training_words:
        #             continue

        #         x, y = parse_dataset_row(word, target, delta)
        #         for letter_idx, letter in enumerate(x):
        #             x[letter_idx]['is_made_up_3'] = 1
        #             x[letter_idx]['noise_length' + str(len(word))] = 1
        #         xs.append(x)
        #        ys.append(y)
    return xs, ys


def score_model(X_test, y_test, y_predicted):
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

    print("f1_score", f1_score)


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

    for delta in DELTAS:
        report['delta'] = delta
        X_train, y_train = load_dataset("task1_data/training.eng.txt", delta=delta, synthetic_data=USE_SYNTETIC_DATA)
        model = crf.CRF(
            algorithm='ap',
            epsilon=10 ** -3,
            max_iterations=1000,
            # algorithm='lbfgs',
            # c1=0.1,
            # c2=0.01,
            # all_possible_transitions=False,
            # all_possible_states=False,
            verbose=True,
        )
        print("fitting {} datapoint".format(len(X_train)))
        model.fit(X_train, y_train)
        print("Xtrain like:", X_train[0][3])
        print("Xnoise like:", X_train[-1][3])
        # print("overfit?", model.score(X_train, y_train))

        print("[SCORING] delta", delta)
        X_test, y_test, = load_dataset("task1_data/dev.eng.txt", delta=delta)
        # print("y like:", y_test[0])
        y_predicted = model.predict(X_test)
        score_model(X_test, y_test, y_predicted)

    print("READ https://en.wikipedia.org/wiki/Morpheme")


if __name__ == "__main__":
    main()
