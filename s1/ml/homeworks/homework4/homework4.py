import random

import numpy as np
import tabulate
from matplotlib.colors import ListedColormap
from pandas import DataFrame
from sklearn.svm import SVC
import math
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import sklearn
from sklearn import neighbors, datasets
import sklearn.cross_validation


def classify_and_plot(X, Y, X_train, y_train, clf, x_test, y_test, show=False):
    score = clf.score(x_test, y_test)
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    h = 0.1 / abs(x_max - x_min)

    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    X_plot = np.c_[xx.ravel(), yy.ravel()]

    Z = clf.predict(X_plot)
    Z = Z.reshape(xx.shape)

    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
    plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

    # Plot also the training points
    cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
    plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cmap_bold)
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.title("kernel:{}_C:{}_score:{}".format(clf.kernel, clf.C, score))
    plt.savefig("kernel:{}_C:{}_score:{}.jpg".format(clf.kernel, clf.C, score))
    if show:
        plt.show()
    return score


def linear_SMV(X, y, x_train, y_train, x_valid, y_valid, x_test, y_test):
    idx = list(range(-3, 4))
    cs = [math.pow(10, i) for i in idx]
    scores = []
    clfs = {}
    for C in cs:
        clf = SVC(C=C, kernel='linear')
        clf.fit(x_train, y_train)
        score = classify_and_plot(X, y, x_train, y_train, clf, x_valid, y_valid)
        print(C, score)
        scores.append(score)
        clfs[C] = clf

    # plt.plot(cs, scores)
    plt.semilogx(cs, scores,
                 basex=10,
                 color='darkred',
                 linewidth=0.5)
    plt.xlim(min(cs) - 1, max(cs) + 1)
    plt.ylim(0, 1)
    plt.title("C vs score")
    plt.savefig("c-tuning_{}.jpg".format(clf.kernel))
    # plt.show()

    best_id = np.argmax(scores)
    best_c = cs[best_id]
    print("best was", best_id, best_c)

    best_clf = clfs[best_c]
    test_score = best_clf.score(x_test, y_test)
    print("test score of best:", test_score)


def RBF_SMV_gamma_c(X, y, x_train, y_train, x_valid, y_valid, x_test, y_test):
    idx_c = list(range(-3, 4))
    idx_g = list(range(-3, 4))
    cs = [math.pow(10, i) for i in idx_c]
    gammas = [math.pow(10, i) for i in idx_g]

    svm = SVC(kernel='rbf')
    """
    for C in cs:
        for g in gammas:
            clf = SVC(C=C, gamma=g, kernel='rbf')
            clf.fit(x_train, y_train)
            score = classify_and_plot(X, y, x_train, y_train, clf, x_valid, y_valid)
            print(C, score)
            scores.append(score)
            clfs[C] = clf
    """
    parameters = {
        'C': cs,
        'gamma': gammas,
    }

    # from sklearn.model_selection import ShuffleSplit
    class fake_iter(object):
        def split(self, X, y):
            t = len(x_train)
            v = int(t * 0.6)
            yield range(t), range(t, t+v)

        def get_n_splits(self, X, y):
            return 1

    clf = GridSearchCV(svm, param_grid=parameters, cv=fake_iter)
    clf.fit(X, y)
    df = DataFrame(clf.cv_results_)
    pretty_table = tabulate.tabulate(df, headers='keys', tablefmt='psql')
    with open("/tmp/gridsearch", "w") as results:
        results.write(pretty_table)
    print("best param", clf.best_params_)
    # best_clf = clf.best_estimator_
    best_clf = SVC(C=clf.best_params_['C'], gamma=clf.best_params_['gamma'], kernel='rbf')
    best_clf.fit(x_train, y_train)
    score = classify_and_plot(X, y, x_train, y_train, best_clf, x_valid, y_valid, show=False)

    """
    plt.semilogx(cs, scores,
                 basex=10,
                 color='darkred',
                 linewidth=0.5)
    # plt.plot(cs, scores)
    plt.xlim(min(cs) - 1, max(cs) + 1)
    plt.ylim(0, 1)
    plt.title("C vs score")
    plt.savefig("c-tuning_{}.jpg".format(clf.kernel))
    # plt.show()

    best_id = np.argmax(scores)
    best_c = cs[best_id]
    print("best was", best_id, best_c)

    best_clf = clfs[best_c]
    test_score = best_clf.score(x_test, y_test)
    print("test score of best:", test_score)
    """


def RBF_SMV_gamma_c_5fold(X, y, x_train, y_train, x_valid, y_valid, x_test, y_test):
    idx_c = list(range(-3, 4))
    idx_g = list(range(-3, 4))
    cs = [math.pow(10, i) for i in idx_c]
    gammas = [math.pow(10, i) for i in idx_g]

    svm = SVC(kernel='rbf')
    """
    for C in cs:
        for g in gammas:
            clf = SVC(C=C, gamma=g, kernel='rbf')
            clf.fit(x_train, y_train)
            score = classify_and_plot(X, y, x_train, y_train, clf, x_valid, y_valid)
            print(C, score)
            scores.append(score)
            clfs[C] = clf
    """
    parameters = {
        'C': cs,
        'gamma': gammas,
    }

    class fake_iter(object):
        def split(self, X, y):
            dataset = list(range(len(X)))
            random.shuffle(dataset)
            train = int(len(dataset) * 0.7)
            yield dataset[:train], dataset[train:]

        def get_n_splits(self, X, y):
            return 5


    clf = GridSearchCV(svm, param_grid=parameters, cv=fake_iter)
    clf.fit(X, y)

    df = DataFrame(clf.cv_results_)
    pretty_table = tabulate.tabulate(df, headers='keys', tablefmt='psql')
    with open("/tmp/gridsearch5fold", "w") as results:
        results.write(pretty_table)
    print("best param, 5fold", clf.best_params_)
    # best_clf = clf.best_estimator_
    best_clf = SVC(C=clf.best_params_['C'], gamma=clf.best_params_['gamma'], kernel='rbf')
    best_clf.fit(x_train, y_train)
    score = classify_and_plot(X, y, x_train, y_train, best_clf, x_valid, y_valid, show=True)

    """
    plt.semilogx(cs, scores,
                 basex=10,
                 color='darkred',
                 linewidth=0.5)
    # plt.plot(cs, scores)
    plt.xlim(min(cs) - 1, max(cs) + 1)
    plt.ylim(0, 1)
    plt.title("C vs score")
    plt.savefig("c-tuning_{}.jpg".format(clf.kernel))
    # plt.show()

    best_id = np.argmax(scores)
    best_c = cs[best_id]
    print("best was", best_id, best_c)

    best_clf = clfs[best_c]
    test_score = best_clf.score(x_test, y_test)
    print("test score of best:", test_score)
    """


def main():
    iris = datasets.load_iris()
    X = iris.data[:, :2]
    y = iris.target

    x_train, x_other, y_train, y_other = sklearn.cross_validation.train_test_split(X, y, test_size=0.5)
    x_test, x_valid, y_test, y_valid = sklearn.cross_validation.train_test_split(x_other, y_other, test_size=0.4)

    # linear_SMV(X, y, x_train, y_train, x_valid, y_valid, x_test, y_test)
    # RBF_SMV_gamma_c(X, y, x_train, y_train, x_valid, y_valid, x_test, y_test)
    RBF_SMV_gamma_c_5fold(X, y, x_train, y_train, x_valid, y_valid, x_test, y_test)


if __name__ == "__main__":
    main()
