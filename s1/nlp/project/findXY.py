from utils import disk_cache

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
    # create spacy graph for given sentence
    tree = parser(question)

    # merge correlated in spacy graph
    for noun in tree.noun_chunks:
        noun.merge(noun.root.tag_, noun.text, noun.root.ent_type_)

    Xs = findX(tree)
    if len(Xs) > 1:
        Xs = [None, ]
    X, = Xs
    Ys = findY(tree, Xs)
    if len(Ys) > 1:
        Ys = [None, ]
    Y, = Ys

    return X, Y
