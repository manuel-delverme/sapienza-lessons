import classify_pattern
import eli5
import pickle
import sklearn.metrics

for model in models:
    model = ??
        eli5.show_weights(model, top=100)
        eli5.explain_prediction(clf, docs[0], vec=vec, target_names=target_names, top=20)
        eli5.explain_weights(clf, docs[0], vec=vec, target_names=target_names, top=20)

stats = {}

for entry in db.find({}):
    question = entry['quesiton']
    domain = entry['quesiton']
    relation = entry['quesiton']
    c1 = entry['quesiton']
    c2 = entry['quesiton']

    y_domain_pred = domain_clf.predict(question)
    y_domain_true = domain

    y_relation_pred = relation_clf.predict(question)
    y_relation_true = relation

    y_xy_pred = xy_clf.predict(question)
    y_xy_true = xy

domain_report = sklearn.metrics.classification_report(y_domain_true, y_domain_pred)# , labels=None, target_names=None, sample_weight=None, digits=2)
print("domain", domain_report)
relation_report = sklearn.metrics.classification_report(y_domain_true, y_domain_pred)# , labels=None, target_names=None, sample_weight=None, digits=2)
print("relation", relation_report)
xy_report = sklearn.metrics.classification_report(y_domain_true, y_domain_pred)# , labels=None, target_names=None, sample_weight=None, digits=2)
print("xy", xy_report)
