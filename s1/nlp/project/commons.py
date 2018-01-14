from disk_utils import disk_cache
import nltk
import tqdm
from enum import Enum
import pprint


class Modality(Enum):
    querying = 1
    enriching = 2


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
            pprint.pprint(tmp_relation_list)
            return list(tmp_relation_list)

        _relation_list = _load_relation_list()
    return _relation_list


def parse_row(entry, stem=False):
    entry = entry.strip("\n").lower()
    if "\t" not in entry:
        if "?" in entry:
            entry = entry.replace("?", "?\t")
        else:
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
    relation_list = load_relation_list()
    if target not in relation_list:
        import difflib
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
    db = mariaDB.Gaia_db('nlp_projectDB', remote=False)
    pos_tags = []
    questions = []
    database = db.db.knowledge_base.find({}, no_cursor_timeout=True)
    # num = 0
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    for row in tqdm.tqdm(database, total=4534082):
        # num += 1
        # print("progress", num / 4534082)
        # if num / 4534082 > 0.00005:
        #     break

        question = row['question']
        c1 = row['c1'].lower()
        c2 = row['c2'].lower()
        if "::" in c1:
            c1 = c1.split("::")[0]
        if "::" in c2:
            c2 = c2.split("::")[0]

        # relation = row['relation'].lower()
        # answer = row['answer'].lower()
        del row

        doc = parser(question)
        for np in doc.noun_chunks:
            np.merge(tag=np.root.tag_, lemma=np.lemma_, ent_type=np.root.ent_type_)

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
    warnings.resetwarnings()
    Xs = []
    Ys = []
    for question, c1, c2 in zip(pos_tags, c1s, c2s):
        seqx = question_to_seqx(question)
        Xs.append(seqx)
        seqy = ["other"] * len(seqx)
        seqy[c1] = "cX"
        seqy[c2] = "cX"
        Ys.append(seqy)
    return Xs, Ys, questions


def question_to_seqx(question):
    seqx = []

    question = ["^"] + question + ["$"]

    for idx in range(1, len(question) - 1):
        x = {
            '0': question[idx],
            '-1': question[idx - 1],
            '+1': question[idx + 1],
            # 'idx': idx
        }
        seqx.append(x)
    return seqx


class DomainDetectionFail(Exception):
    pass


class ModalityDetectionFail(Exception):
    pass


class FailToAnswerException(Exception):
    pass


class RelationDetectionFail(Exception):
    pass
