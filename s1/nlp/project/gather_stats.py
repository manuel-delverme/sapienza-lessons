import classify_pattern
import answer_question
import eli5
import pickle
import sklearn.metrics
import pymongo
import tqdm
import main


def gather_stats():
    client = pymongo.MongoClient('localhost')
    db = client['nlp_projectDB']['knowledge_base']

    stats = {}

    query = {'domain': {'$ne': ['', ]}}
    results = db.find(query)
    for entry in tqdm.tqdm(results, total=db.count(query)):
        question = entry['question']
        domains = entry['domains']
        relation = entry['relation']
        c1 = entry['c1']
        c2 = entry['c2']

        if domains != ['', ]:
            domain_hat, conference = main.MariaBot.classify_domain(question)
            print(domain_hat, domains, conference)
            if domain_hat in domains:
                stats['domain']['correct'] += 1
            else:
                stats['domain']['false'] += 1
        # relation_hat = classify_domain(question)

        # answer = answer_question.answer_question(db, question, relation)
        # # self.relation = None

        # y_domain_pred = domain_clf.predict(question)
        # y_domain_true = domain

        # y_relation_pred = relation_clf.predict(question)
        # y_relation_true = relation

        # y_xy_pred = xy_clf.predict(question)
        # y_xy_true = xy

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


if __name__ == '__main__':
    gather_stats()
