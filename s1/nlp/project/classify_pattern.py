import glob
import difflib
from sklearn.preprocessing import normalize
import pickle
import nltk
import numpy as np

with open("chatbot_maps/domains_to_relations.tsv") as fin:
    # Philosophy and psychology	activity	similarity	time	generalization	size	specialization	part
    domain_list = []
    for row in fin:
        domain_list.extend(row.strip("\n").lower().split("\t")[1:])
    domain_list = set(domain_list)
    domain_list.remove("")


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
