from disk_utils import disk_cache
import pprint

_parser = None


def parser(text):
    global _parser
    if _parser is None:
        import spacy
        _parser = spacy.load('en_core_web_lg')
    return _parser(text)


_relation_list = None


def load_relation_list():
    global _relation_list
    if _relation_list is None:
        @disk_cache
        def _load_relation_list():
            with open("chatbot_maps/domains_to_relations.tsv") as fin:
                tmp_relation_list = set()
                for row in fin:
                    relations = row.strip("\n").lower().split("\t")[1:]
                    tmp_relation_list.update(relations)
            print("loaded domain list")
            if "" in tmp_relation_list:
                tmp_relation_list.remove("")
            pprint.pprint(_relation_list)
            return list(_relation_list)

        _relation_list = _load_relation_list()
    return _relation_list


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

@disk_cache
def load_data():
    import mariaDB
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


