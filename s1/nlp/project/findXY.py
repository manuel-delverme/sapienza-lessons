from disk_utils import disk_cache
import itertools
import commons
import glob
import nltk
import sklearn_crfsuite as crf
from sklearn import model_selection


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
                    question, target = commons.parse_row(row)
                except ValueError as e:
                    print("[LOAD_PATTERN_DICT] DROPPING", row, e)
                    continue
                sub_dict = pattern_dict
                for word in question:
                    if word not in sub_dict:
                        sub_dict[word] = {}
                    sub_dict = sub_dict[word]
                sub_dict["$END$"] = (question, target)
    return pattern_dict


def bruteforce_findCHAR(tree, sentence, what, depth=0):
    assert isinstance(sentence, list)
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
    question = nltk.word_tokenize(question.lower())
    startXs = bruteforce_findX(pattern_tree, question)
    Xs = []
    Ys = [None, ]
    for startX in startXs:
        subtreeX = pattern_tree
        # walk the tree until the beginning of the potential X
        for word in question[:startX]:
            subtreeX = subtreeX[word]
        subtreeX = subtreeX['x']

        # for each potential final X
        for endX in range(startX + 1, len(question)):
            candidateX = question[startX: endX]
            unmatched_question = question[endX:]

            startYs = bruteforce_findY(subtreeX, unmatched_question)
            # look for an Y from X to
            if len(startYs) > 0:
                # if there will be a Y down the tree
                # add the candidate and start matching the Y
                Xs.append(candidateX)

                for startY in startYs:
                    startY += endX
                    # print("found Y!", startYs, "X=", question[startX: endX],
                    #      "Y=>{}? who knows".format(question[startY:]))
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
            # else:
            #     pass
            #     # print("not a valid X",
            #     #      "{}  [{}]  {}".format(" ".join(question[:startX]), " ".join(question[startX: endX]),
            #     #                            " ".join(question[endX:])))

            # is the unmatched part still in the tree? if not, then the pattern doesn't match
            if match_end_of_string(unmatched_question, subtreeX):
                Xs.append(" ".join(candidateX))

    print("Xs", Xs)
    print("Ys", Ys)
    return Xs, Ys


def match_end_of_string(subquestion, subtree):
    return len(bruteforce_findEND(subtree, subquestion)) > 0


@disk_cache
def tag_question(question, use_spacy=True):
    # import ipdb; ipdb.set_trace()
    words = []
    tags = []
    if use_spacy:
        doc = commons.parser(question)
        for np in doc.noun_chunks:
            np.merge(tag=np.root.tag_, lemma=np.lemma_, ent_type=np.root.ent_type_)
        for token in doc:
            words.append(token.text)
            tags.append(token.pos_)
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
    results = {
        'bruteforce': bruteforce_findXY(question)
    }
    words, tags = tag_question(question)
    seqx = commons.question_to_seqx(tags)
    # merge same consecutive tags
    model = load_model()
    y_hat, = model.predict([seqx])
    candidates = set([None])
    for idx, y_i in enumerate(y_hat):
        if y_i[0] == "c":
            candidates.add(words[idx])

    results['crf'] = [x for x in itertools.permutations(candidates, r=2) if x[0] is not None]
    return results


def test_findXY():
    Xs, Ys, questions = commons.load_data()
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


@disk_cache
def load_model():
    print("training model")
    Xs, Ys, _ = commons.load_data()
    assert len(Xs) > 0
    for idx, y in enumerate(Ys):
        lala = "c1"
        for idxi, yi in enumerate(y):
            if yi[0] == "c":
                Ys[idx][idxi] = lala
                lala = "c2"
    X_train, _, y_train, _ = model_selection.train_test_split(Xs, Ys, test_size=0.3)
    model = crf.CRF(
        algorithm='ap',
    )
    model.fit(X_train, y_train)
    return model


if __name__ == "__main__":
    X, Y = bruteforce_findXY([
        "what",
        "is",
        "the",
        "form",
        "of",
        "love",
        "?",
    ])
    # test_findXY()
