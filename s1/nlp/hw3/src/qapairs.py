import pickle
import urllib
import glob

questions = {
    'similar to': [
        "if i were to see {} what could i mistake it for?",
        "what can {} be mistaken for?",
        "what does {} look like?",
        "what's something similar to {}?",
        "{}? you mean what's is it like?",
    ],
    'part': [
        "what's a part of {}?",
        "what's inside {}?",
        "{} is made by?",
        "what you can recover from {}?",
        "without what {} would not be the same?",
    ],
    'activity': [
        "if you were a {} would you be able to do?",
        "what do {} can do?",
        "what have you seen {} do?",
        "somewhere in the universe, there is a {} doing what?",
    ],
    'taste': [
        "if you ate a {} what would it taste like?",
        "how does {} taste like?",
        "if i like the taste of {}, what else could i like?",
    ],
    'color': [
        "roses are red violets are blue, {} is ?",
        "what's the color of {}?",
        "if i were to fill a container of {} what color would that be?",
    ]
}
with open("patterns.tsv", "w") as fout:
    for relation, qs in questions.items():
        for q in qs:
            fout.write("{} \t {}\n".format(q.format("X", "Y"), relation))

relation_lookup = {
    'has': 'part',
    'similar to': 'similar to',
    'similar': 'similar to',
    'color': 'color',
    'tastes like': 'taste',
    'tastes': 'taste',
    'able': 'activity',
}
context = {}
for name in questions.keys():
    f_name = name
    if name == "similar to":
        f_name = "confused"
    elif name == "taste":
        f_name = "tastes"
    with open("results/context_{}".format(f_name), 'rb') as fin:
        context[name] = dict(pickle.load(fin))

i = 0
with open("triples.tsv", "w") as triplesf:
    with open("qap.tsv", "w") as qapf:
        for result_file in glob.glob("results/*"):
            if "context_" in result_file:
                continue
            with open(result_file) as fin:
                for result_tuple in fin:
                    tuple_row = result_tuple[:-1]
                    x, relation, y = tuple_row.split(", ")
                    triplesf.write("{} \t {} \t {}\n".format(*map(urllib.parse.unquote, (x, relation_lookup[relation], y))))

                    if "color" in result_file:
                        tup_context = ""
                    else:
                        relation_key = relation_lookup[relation]
                        rel_context = context[relation_key]
                        tup_context = sorted(rel_context[tuple_row], key=len)[0]

                    if ":WIKIPAGE" in x:
                        x = x.split(":")[0]
                        x_bid = ""
                    elif ":" in x:
                        x, bn, x_bid = x.split(":")
                        x_bid = bn + ":" + x_bid
                    else:
                        x, x_bid = x, ""

                    if ":WIKIPAGE" in y:
                        y = y.split(":")[0]
                        y_bid = ""
                    elif ":" in y:
                        y, bn, y_bid = y.split(":")
                        y_bid = bn + ":" + y_bid
                    else:
                        y, y_bid = y, ""

                    answer = urllib.parse.unquote(y)
                    x = urllib.parse.unquote(x)
                    relation = relation_lookup[relation]
                    source = tup_context

                    for question_pattern in questions[relation]:
                        question = question_pattern.format(x)
                        row = "{} \t {} \t {} \t {} \t {} {}\n".format(question, answer, relation, source, x_bid, y_bid)
                        i += 1
                        print(i)
                        qapf.write(row)
