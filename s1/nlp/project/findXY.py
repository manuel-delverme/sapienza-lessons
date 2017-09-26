from utils import disk_cache
import numpy as np
import nltk
import sklearn_crfsuite as crf
from sklearn import model_selection

# with open("/BabelDomains_full/domain_list.txt") as fin:
#    domain_list = []
#    for row in fin:
#        domain_list.extend(row.strip("\n").lower().split("\t")[1:])

_parser = None


def parser(text):
    global _parser
    if _parser is None:
        import spacy
        _parser = spacy.load('en_core_web_md')
    return _parser(text)


def findX(tree):
    Xs = []
    for elem in tree:
        if "subj" in elem.dep_:
            Xs.append(elem.string)
    if not Xs:
        for elem in tree:
            if "obj" in elem.dep_:
                Xs.append(elem.string)
    if not Xs:
        for elem in tree:
            if "comp" in elem.dep_:
                Xs.append(elem.string)
    if not Xs:
        return [None, ]
    return Xs


def findY(tree, Xs):
    Ys = []
    for elem in tree:
        if "obj" in elem.dep_ and elem not in Xs:
            Ys.append(elem.txt_)
    if not Ys:
        for elem in tree:
            if "comp" in elem.dep_ and elem not in Xs:
                Ys.append(elem.txt_)
    if not Ys:
        for elem in tree:
            if "attr" in elem.dep_:
                Ys.append(elem.txt_)

    if not Ys:
        return [None, ]
    return Ys


@disk_cache
def findXY(question, use_spacy=False):
    if use_spacy:
        tree = to_spacy_tree(question)
        Xs = findX(tree)
    else:
        tree = nltk.pos_tag()
        Xs = findX(tree)

    if len(Xs) > 1:
        Xs = [None, ]
    X, = Xs
    Ys = findY(tree, Xs)
    if len(Ys) > 1:
        Ys = [None, ]
    Y, = Ys

    return X, Y


def to_spacy_tree(question):
    # create spacy graph for given sentence
    tree = parser(question)
    # merge correlated in spacy graph
    for noun in tree.noun_chunks:
        noun.merge(noun.root.tag_, noun.text, noun.root.ent_type_)
    return tree


def test_findXY():
    Xs, Ys = load_data()
    X_train, X_test, y_train, y_test = model_selection.train_test_split(Xs, Ys, test_size=0.3)
    model = crf.CRF()
    model.fit(X_train, y_train)
    y_hat = model.predict(X_test)
    score = 0
    for sentence, sentence_ in zip(y_hat, y_test):
        if all(y == y_ for y, y_ in zip(sentence, sentence_)):
            score += 1
    print("score", score / len(y_hat))


# @disk_cache
def load_data():
    c1s = []
    c2s = []
    pos_tags = []
    with open("babelData.tsv", "r") as database:
        for row in database:
            entry = row.strip()
            entry = entry.strip("\n")

            question, answer, relation, c1, c2, context, = entry.split("\t")
            question = nltk.word_tokenize(question)
            tagged_words = nltk.pos_tag(question)
            if "::" in c1:
                c1 = c1.split("::")[0]
            if "::" in c2:
                c2 = c2.split("::")[0]

            idx1 = None
            idx2 = None
            tags = []
            for idx, tagged_word in enumerate(tagged_words):
                word, tag = tagged_word
                tags.append(tag)
                if word == c1:
                    idx1 = idx
                if word == c2:
                    idx2 = idx
            if idx1 is not None and idx2 is not None:
                c1s.append(idx1)
                c2s.append(idx2)
                pos_tags.append(tags)
    Xs = []
    Ys = []
    for question, c1, c2 in zip(pos_tags, c1s, c2s):
        seqx = []
        seqy = []
        for idx, q in enumerate(question):
            x = {'0': question[idx], }
            if idx > 0:
                x['-1'] = question[idx - 1]
            else:
                x['-1'] = "^"

            if (idx + 1) < len(question):
                x['+1'] = question[idx + 1]
            else:
                x['+1'] = "$"

            if idx == c1:
                tag = "c1"
            elif idx == c2:
                tag = "c2"
            else:
                tag = "other"
            seqx.append(x)
            seqy.append(tag)
        Xs.append(seqx)
        Ys.append(seqy)
    return Xs, Ys


if __name__ == "__main__":
    test_findXY()
