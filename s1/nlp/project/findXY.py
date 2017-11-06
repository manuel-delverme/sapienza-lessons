from utils import disk_cache
import re
import difflib
import glob
import pprint
from collections import defaultdict
import mariaDB
import numpy as np
import nltk
import sklearn_crfsuite as crf
from sklearn import model_selection


@disk_cache
def load_relation_list():
    with open("chatbot_maps/domains_to_relations.tsv") as fin:
        _relation_list = set()
        for row in fin:
            relations = row.strip("\n").lower().split("\t")[1:]
            _relation_list.update(relations)
    print("loaded domain list")
    if "" in _relation_list:
        _relation_list.remove("")
    pprint.pprint(_relation_list)
    return list(_relation_list)


relation_list = load_relation_list()

_parser = None


def parser(text):
    global _parser
    if _parser is None:
        import spacy
        _parser = spacy.load('en_core_web_sm')
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
def load_pattern_dict():
    print("parsing pattern dict")
    pattern_dict = {}
    for file_name in glob.glob("patterns/*"):
        print("FILE:", file_name)
        with open(file_name) as fin:
            for row in fin:
                try:
                    question, target = parse_row(row)
                except ValueError as e:
                    print("DROPPING", row, e)
                    continue
                sub_dict = pattern_dict
                for word in question:
                    if word not in sub_dict:
                        sub_dict[word] = {}
                    sub_dict = sub_dict[word]
                sub_dict["$END$"] = (question, target)
    return pattern_dict


def bruteforce_findCHAR(tree, sentence, what, depth=0):
    idxs = []
    leaves = list(tree.keys())
    if what in leaves:
        idxs = [depth]

    if len(sentence) > 0:
        word = sentence[0]
        if word in leaves:
            hits = bruteforce_findCHAR(tree[word], sentence[1:], what, depth + 1)
            idxs.extend(hits)
    return idxs


def bruteforce_findX(tree, sentence):
    return bruteforce_findCHAR(tree, sentence, what="x")


def bruteforce_findY(tree, sentence):
    return bruteforce_findCHAR(tree, sentence, "y")


def bruteforce_findEND(tree, sentence):
    return bruteforce_findCHAR(tree, sentence, "$END$")


def bruteforce_findXY(question):
    pattern_tree = load_pattern_dict()
    startXs = bruteforce_findX(pattern_tree, question)
    Xs = []
    Ys = []
    for startX in startXs:
        subtreeX = pattern_tree
        for word in question[:startX]:
            subtreeX = subtreeX[word]
        subtreeX = subtreeX['x']
        for endX in range(startX + 1, len(question)):
            startYs = bruteforce_findY(subtreeX, question[endX:])
            # look for an Y from X to
            if len(startYs) > 0:
                Xs.append(question[startX: endX])

                for startY in startYs:
                    startY += endX
                    print("found Y!", startYs, "X=", question[startX: endX],
                          "Y=>{}? who knows".format(question[startY:]))
                    subtreeY = subtreeX

                    for word in question[endX:startY]:
                        subtreeY = subtreeY[word]
                    subtreeY = subtreeY['y']

                    for endY in range(startY + 1, len(question)):
                        tentativeY = question[startY: endY]
                        subquestion = question[endY:]
                        if match_end_of_string(subquestion, subtreeY):
                            Ys.append(tentativeY)
                        subtreeY = subtreeY[question[endY]]
            else:
                print("not a valid X",
                      "{}  [{}]  {}".format(" ".join(question[:startX]), " ".join(question[startX: endX]),
                                            " ".join(question[endX:])))
            # look for an $END$ from X on
            if match_end_of_string(question[endX:], subtreeX):
                print("FOUND END! valid X",
                      "{}  [{}] $$$".format(" ".join(question[:startX]), " ".join(question[startX:])))
                Xs.append(question[startX: endX])
            else:
                print("not a valid X", "{}  [{}] $$$".format(" ".join(question[:startX]), " ".join(question[startX:])))
    print("Xs", Xs)
    print("Ys", Ys)
    return Xs, Ys


def match_end_of_string(subquestion, subtree):
    return len(bruteforce_findEND(subtree, subquestion)) > 0


def parse_row(entry, stem=False):
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
    if "2" in target:
        target = target.replace("2", "to")
    if "is" in target and "a" in target:
        target = "generalization"

    question = nltk.tokenize.word_tokenize(question)
    if stem:
        sno = nltk.stem.SnowballStemmer('english')
        question = [sno.stem(word) for word in question]
    if target not in relation_list:
        try:
            new_target, = difflib.get_close_matches(target, relation_list, n=1)
        except ValueError:
            for relation in relation_list:
                if target in relation:
                    new_target = relation
                    break
            else:
                print(target, "is not a relationship")
                raise ValueError()
        target = new_target
    return question, target


def tag_question(question, use_spacy=True):
    if use_spacy:
        parser(question)
    else:
        question = nltk.word_tokenize(question)
        question_ = ['']
        for word in question:
            if (word in c1 or word in c2) and (question_[-1] in c1 or question_[-1] in c2):
                question_[-1] += " " + word
            else:
                question_.append(word)

        if question_[0] == '':
            del question_[0]
        question = question_
        tagged_words = nltk.pos_tag(question)

        from nltk.tag import StanfordPOSTagger
        spos = StanfordPOSTagger("spos/models/english-bidirectional-distsim.tagger",
                                 path_to_jar="spos/stanford-postagger.jar")
        print("SKPPING WORD MERGING")
        tagged_words = nltk.pos_tag(question)
        words, tags = zip(*tagged_words)
    return words, tags


# @disk_cache
def findXY(question):
    Xs = bruteforce_findXY(question)
    words, tags = tag_question(question)
    seqx, _ = question_to_seqx(list(tags))
    # merge same consecutive tags
    model = load_model()
    y_hat, = model.predict([seqx])
    X, Y = None, None
    for idx, y_i in enumerate(y_hat):
        if y_i == "c1":
            X = idx
            break

    for idx, y_i in enumerate(reversed(y_hat)):
        if y_i == "c2":
            Y = idx
            break
    return X, Y


def test_findXY():
    Xs, Ys, questions = load_data()
    # _, X_test, _, y_test = model_selection.train_test_split(Xs, Ys, test_size=0.3)
    model = load_model()
    y_hat = model.predict(X_test)
    score = 0
    for sentence, sentence_ in zip(y_hat, y_test):
        # sentence = [s.replace("2", "1") for s in sentence[:-1]]
        # sentence_ = [s.replace("2", "1") for s in sentence_[:-1]]
        if sentence == sentence_:
            score += 1
    print("score", score / len(y_hat))


# @disk_cache
def load_model():
    print("training model")
    Xs, Ys, _ = load_data()
    X_train, _, y_train, _ = model_selection.train_test_split(Xs, Ys, test_size=0.3)
    model = crf.CRF()
    model.fit(X_train, y_train)
    return model


@disk_cache
def load_data():
    c1s = []
    c2s = []
    db = mariaDB.Gaia_db('nlp_projectDB')
    pos_tags = []
    questions = []
    database = db.db.knowledge_base.find({}, no_cursor_timeout=True)
    num = 0
    for row in database:
        num += 1
        print("progress", num / 4534082)
        if num / 4534082 > 0.05:
            break

        question = row['question']
        c1 = row['c1'].lower()
        c2 = row['c2'].lower()
        if "::" in c1:
            c1 = c1.split("::")[0]
        if "::" in c2:
            c2 = c2.split("::")[0]

        relation = row['relation'].lower()
        answer = row['answer'].lower()
        del row

        doc = parser(question)
        for noun in doc.noun_chunks:
            noun.merge(noun.root.tag_, noun.text, noun.root.ent_type_)

        idx1 = None
        idx2 = None
        tags = []
        for idx, chunk in enumerate(doc):
            tag = chunk.pos_
            word = chunk.text
            tags.append(tag)
            if word.lower() == c1.lower():
                idx1 = idx
            if word.lower() == c2.lower():
                idx2 = idx
        if idx1 is not None and idx2 is not None:
            c1s.append(idx1)
            c2s.append(idx2)
            pos_tags.append(tags)
            questions.append(question)
    Xs = []
    Ys = []
    for question, c1, c2 in zip(pos_tags, c1s, c2s):
        seqx, seqy = question_to_seqx(question, c1, c2)
        Xs.append(seqx)
        Ys.append(seqy)
    return Xs, Ys, questions


def question_to_seqx(question, c1=None, c2=None):
    seqx = []
    seqy = []

    question = ["^"] + question + ["$"]
    c1 += 1
    c2 += 1

    for idx in range(1, len(question) - 1):
        x = {
            '0': question[idx],
            '-1': question[idx - 1],
            '+1': question[idx + 1],
            # 'idx': idx
        }
        seqx.append(x)
        if c1 and c2:
            if idx == c1:
                tag = "c1"
            elif idx == c2:
                tag = "c2"
            else:
                tag = "other"
            seqy.append(tag)
    return seqx, seqy


if __name__ == "__main__":
    bruteforce_findXY([
        "what",
        "is",
        "the",
        "form",
        "of",
        "love",
        "?",
    ])
    # test_findXY()
