from utils import disk_cache
import sklearn_crfsuite as crf

with open("babelData.tsv") as fin:
    domain_list = []
    for row in fin:
        domain_list.extend(row.strip("\n").lower().split("\t")[1:])

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
def findXY(question):
    tree = to_spacy_tree(question)
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


def train_crf(questions, c1s, c2s):
    word_deps = []
    tags = []
    for q, c1, c2 in zip(questions, c1s, c2s):
        tree = to_spacy_tree(q)
        for elem in tree:
            word_deps.append(elem._dep)
            if c1 == elem.txt_:
                tag = "c1"
            if c2 == elem.txt_:
                tag = "c2"
            else:
                tag = "other"
            tags.append(tag)
    model = crf.CRF()
    model.fit(word_deps, tags)



def test_findXY():
    Xs = []
    Ys = []
    questions = []
    with open("babelData.tsv", "r") as database:
        for row in database:
            entry = row.strip()
            entry = entry.strip("\n")

            question, answer, relation, c1, c2, context, = entry.split("\t")
            questions.append(question)
            Xs.append(c1)
            Ys.append(c2)
    train_crf(questions, Xs, Ys)

    x_score = 0
    y_score = 0
    entries = 0
    with open("babelData.tsv", "r") as database:
        for row in database:
            entry = row.strip()
            entry = entry.strip("\n")

            question, answer, relation, c1, c2, context, = entry.split("\t")
            x, y = findXY(question)
            entries += 1
            if x == c1:
                x_score += 1
            if y == c2:
                y_score += 1
    print("x_score", x_score/entries, "y_score", y_score/entries)
