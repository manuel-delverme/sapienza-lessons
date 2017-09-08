from findXY import findXY
from utils import disk_cache


@disk_cache
def answer_question(question, question_relation):
    X, Y = findXY(question)
    is_open_question = Y is None

    with open("babelData.tsv", "r") as database:
        for row in database:
            entry = row.strip()
            entry = entry.strip("\n")

            # question, answer, relation, c1, c2, context, domains, = entry.split("\t")
            question, answer, relation, c1, c2, context, = entry.split("\t")

            if c1 == X and is_open_question:
                return c2

            if c1 == X and not is_open_question:
                return "yes"

    if is_open_question:
        return "i don't know"
    else:
        return "no"
