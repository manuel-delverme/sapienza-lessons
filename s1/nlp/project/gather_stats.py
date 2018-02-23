import classify_pattern
import answer_question
import eli5
import pickle
import sklearn.metrics
import pymongo
import tqdm


def classify_domain(msg_txt):
    # raise DomainDetectionFail()
    with open("chatbot_maps/domain_list.txt") as fin:
        possible_domains = fin.read()[:-1].split("\n")

    classified_domains = collections.OrderedDict({d: 0 for d in possible_domains})
    for word in nltk.tokenize.word_tokenize(msg_txt):
        # print("[BOT] word:", word, "-" * 100)
        total_weight = 0
        weights = {}

        for d in possible_domains:
            try:
                weight = domain_vectors[d][word]
            except KeyError:
                pass
            else:
                # total_weight += math.log(weight)
                weights[d] = weight
        if weights:
            for d in weights.keys():
                classified_domains[d] += weights[d] / (len(weights) ** 2)

    result = sorted(classified_domains, key=lambda x: classified_domains[x], reverse=True)
    best_guess = result[0]
    if classified_domains[best_guess] < 1.5:  # HYPER PARAM
        print("[BOT] domain for question: ", best_guess, classified_domains[best_guess])
        print("[BOT] failed confidence < 1.5")
        raise commons.DomainDetectionFail()
    return best_guess


def main():
    client = pymongo.MongoClient('localhost')
    db = client['nlp_projectDB']['knowledge_base']

    stats = {}

    for entry in tqdm.tqdm(db.find(), total=db.count()):
        question = entry['quesiton']
        domain = entry['quesiton']
        relation = entry['quesiton']
        c1 = entry['quesiton']
        c2 = entry['quesiton']

        domain_hat = classify_domain(question)
        # relation_hat = classify_domain(question)
        answer = answer_question.answer_question(db, question, relation)
        # self.relation = None

        y_domain_pred = domain_clf.predict(question)
        y_domain_true = domain

        y_relation_pred = relation_clf.predict(question)
        y_relation_true = relation

        y_xy_pred = xy_clf.predict(question)
        y_xy_true = xy

    domain_report = sklearn.metrics.classification_report(y_domain_true,
                                                          y_domain_pred)  # , labels=None, target_names=None, sample_weight=None, digits=2)
    print("domain", domain_report)
    relation_report = sklearn.metrics.classification_report(y_domain_true,
                                                            y_domain_pred)  # , labels=None, target_names=None, sample_weight=None, digits=2)
    print("relation", relation_report)
    xy_report = sklearn.metrics.classification_report(y_domain_true,
                                                      y_domain_pred)  # , labels=None, target_names=None, sample_weight=None, digits=2)
    print("xy", xy_report)

    # for model in models:
    #     model = ??
    #     eli5.show_weights(model, top=100)
    #     eli5.explain_prediction(clf, docs[0], vec=vec, target_names=target_names, top=20)
    #     eli5.explain_weights(clf, docs[0], vec=vec, target_names=target_names, top=20)


if __name_ _ == '__main__':
    main()
