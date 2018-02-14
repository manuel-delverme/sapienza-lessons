from findXY import findXY
from askgoogle import ask_google
from disk_utils import disk_cache
import re
import nltk
import itertools


# @disk_cache
def lookup_knowledge_base(db, question_relation, X, Y):
    answers = []
    if "?" in (X, Y):
        return answers

    is_open_question = Y is None

    # re_c = re.compile(r"^{}.*".format(X))
    query = {
        'c1': X,
        # 'c1': re_c,
        # 'relation': question_relation.upper(),
    }
    if not is_open_question:
        query['c2'] = Y # re.compile("^{}.*".format(Y))

    for row in db.find(query):
        c1 = row['c1']
        c2 = row['c2']
        answer = row['answer']

        if is_open_question:
            answer = c2
        if c1 == X and not is_open_question:
            answer = "yes"
        print("matched", row)
        answers.append(answer)
    return answers


def bruteforce_kb(db, question, question_relation):
    question = nltk.word_tokenize(question)
    question.append(None)

    answers = []

    for X, Y in itertools.product(question, repeat=2):
        if X is Y:
            continue
        if X is None:
            continue

        answer = lookup_knowledge_base(db, question_relation=question_relation, X=X, Y=Y)
        if len(answer) > 0:
            answers.append(answer)
    return answers


def classify_lookup_knowledge_base(db, question, question_relation):
    xy_tuples = findXY(question)
    parsed = set()
    for X, Y in itertools.chain(xy_tuples['crf'], xy_tuples['bruteforce']):
        if (X, Y) not in parsed:
            for answer in lookup_knowledge_base(db, question_relation, X, Y):
                yield answer
            parsed.add((X, Y))


# @disk_cache
def answer_question(db, question, question_relation):
    for answer in classify_lookup_knowledge_base(db, question, question_relation):
        return answer
    for answer in bruteforce_kb(db, question, question_relation):
        return answer
    answer = ask_google(db, question, question_relation)
    if answer is not None:
        return answer
    # return "i don't know :("
