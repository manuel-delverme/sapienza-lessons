from findXY import findXY
from askgoogle import ask_google
from disk_utils import disk_cache
import re
import nltk
import itertools


def lookup_knowledge_base(db, question_relation, X, Y):
    answers = []
    is_open_question = Y is None

    re_c = re.compile(r"^{}.*".format(X), re.IGNORECASE)
    query = {
        'c1': re_c,
        'relation': question_relation.upper(),
    }
    if not is_open_question:
        query['c2'] = re.compile("^{}.*".format(Y), re.IGNORECASE)

    for row in db.find(query):
        question = row['question']
        c1 = row['c1']
        c2 = row['c2']
        relation = row['relation']
        answer = row['answer']

        if is_open_question:
            answer = c2
        if c1 == X and not is_open_question:
            answer = "yes"
        answers.append(answer)

    if not answers:
        del query['relation']
        extra_answers = db.db.knowledge_base.find(query)

        for row in extra_answers:
            question = row['question']
            c1 = row['c1']
            c2 = row['c2']
            relation = row['relation']
            answer = row['answer']
            if c1 == X and is_open_question:
                answers.append(c2)

            if c1 == X and not is_open_question:
                answers.append("yes")
    return answers


def bruteforce_kb(db, question, question_relation):
    question = nltk.word_tokenize(question)
    question.append(None)

    for X, Y in itertools.product(question, repeat=2):
        if X is None:
            continue
        is_open_question = Y is None

        X = re.compile("^{}.*".format(X), re.IGNORECASE)
        Y = re.compile("^{}.*".format(Y), re.IGNORECASE)
        return lookup_knowledge_base(db, question_relation=question_relation, X=X, Y=Y)


def classify_lookup_knowledge_base(db, question, question_relation):
    xy_tuples = findXY(question)
    answers = []
    for X, Y in xy_tuples['crf']:
        answers.extend(lookup_knowledge_base(db, question_relation, X, Y))
    print("what about", xy_tuples['bruteforce'], "????")
    return answers


# @disk_cache
def answer_question(db, question, question_relation):
    strategies = [
        classify_lookup_knowledge_base,
        bruteforce_kb,
        ask_google,
    ]
    answers = []
    for strategy in strategies:
        print("[BOT] trying to answer using", strategy)
        answers.extend(strategy(db, question, question_relation))

    if not answers:
        answers = ["i don't know / no"]
    return answers
