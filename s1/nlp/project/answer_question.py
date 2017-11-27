from findXY import findXY
from disk_utils import disk_cache
import re
import nltk
import itertools


# @disk_cache
def answer_question(db, question, question_relation):
    question = nltk.word_tokenize(question)
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
    if not results:
        print("brutefocing X,Y")
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

    # """
    # if is_open_question:
    #     return "i don't know / no"
    # else:
    #     return "no"
    # """
    return "i don't know / no"
