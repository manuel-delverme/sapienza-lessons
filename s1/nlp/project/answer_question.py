from findXY import findXY
from disk_utils import disk_cache
import re
import nltk
import itertools


def lookup_knowledge_base(question):
    X, Y = findXY(question)
    is_open_question = Y is None

    question.append(None)

    X = re.compile("^{}.*".format(X), re.IGNORECASE)
    if not is_open_question:
        Y = re.compile("^{}.*".format(Y), re.IGNORECASE)
    results = db.db.knowledge_base.find({
        'c1': X,
        'c2': Y,
        'relation': question_relation.upper(),
    })
    return results

def bruteforce_xy(question):
    question = nltk.word_tokenize(question)
    for X, Y in itertools.product(question, repeat=2):
        if X is None:
            continue
        is_open_question = Y is None

        # pos_tags = []
        X = re.compile("^{}.*".format(X), re.IGNORECASE)
        Y = re.compile("^{}.*".format(Y), re.IGNORECASE)
        # db.knowledge_base.find({
        #     'relation': 'TASTE',
        #     'c1': reg,
        # })
        results = db.db.knowledge_base.find({
            'c1': X,
            'c2': Y,
            'relation': question_relation.upper(),
        })
        for row in results:
            question = row['question']
            c1 = row['c1']
            c2 = row['c2']
            relation = row['relation']
            answer = row['answer']

            if c1 == X and is_open_question:
                return c2

            if c1 == X and not is_open_question:
                return "yes"


# @disk_cache
def answer_question(db, question, question_relation):
    strategies = [
        lookup_knowledge_base,
        bruteforce_kb,
        ask_google,
    ]
    for strategy in strategies:
        answer = strategy(question)
    else:
        answer = "i don't know / no"
    return answer
