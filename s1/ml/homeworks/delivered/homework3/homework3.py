import numpy as np
from pandas import DataFrame
import tabulate
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

import sys

sys.path.insert(0, '../../')
import sklearn
from sklearn import neighbors, datasets
from matplotlib.colors import ListedColormap
from homeworks.homework1.homework1 import normalize, dim_reduction

iris = datasets.load_iris()
X = iris.data
y = iris.target


def classify_and_outofmemory(show=False):
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1

    clf = worst_knn_ever()
    clf.fit(X_train, y_train)

    xx, yy = np.meshgrid(np.arange(x_min, x_max, 1), np.arange(y_min, y_max, 1))
    X_plot = np.c_[xx.ravel(), yy.ravel()]
    # X_plot = preprocess(X_plot, None, dims=X_train.shape[1])

    Z = clf.predict(X_plot)
    Z = Z.reshape(xx.shape)

    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
    plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

    # Plot also the training points
    cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
    plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cmap_bold)
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    title = "ws = {}, k = {}".format(ws, k)
    plt.title(title)
    print(title, score)
    plt.savefig(title + ".jpg")
    if show:
        plt.show()


class worst_knn_ever(object):
    def fit(self, Xs, Ys):
        self.Xs = np.tile(Xs, Xs.shape[0])
        self.Ys = Ys
    def predict(self, x):
        x_prime = np.zeros((self.Xs.shape[0], x.shape[1]))
        x_prime[:x.shape[0], :x.shape[1]] = x
        b = x_prime.reshape((1, -1)).repeat(self.Xs.shape[0], axis=0)
        dist_map = self.Xs - b
        dist_map = np.power(dist_map, 2)
        classes = []
        last = x.shape[0] * x.shape[1]
        for i in range(0, last, x.shape[1]):
            extractor = np.zeros(self.Xs.shape[0] * x.shape[1])
            extractor[i:i + x.shape[1]] = 1
            distances = dist_map.dot(extractor)
            classes.append(self.Ys[np.argmin(distances)])
        return classes


def classify_and_plot(k, ws="uniform", show=False, ws_name=None):
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    h = 0.1 / abs(x_max - x_min)

    clf = neighbors.KNeighborsClassifier(k, weights=ws)
    clf.fit(X_train, y_train)

    score = clf.score(X_test, y_test)
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    X_plot = np.c_[xx.ravel(), yy.ravel()]
    # X_plot = preprocess(X_plot, None, dims=X_train.shape[1])

    Z = clf.predict(X_plot)
    Z = Z.reshape(xx.shape)

    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
    plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

    # Plot also the training points
    cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
    plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cmap_bold)
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    if ws_name:
        title = "ws={},k={}".format(ws_name, k)
    else:
        title = "ws={},k={}".format(ws, k)
    plt.title(title)
    print(title, score)
    plt.savefig(title + ".jpg")
    if show:
        plt.show()


def preprocess(X, y, dims=False):
    X = normalize(X)
    X = dim_reduction(X, y, force_dims=dims)
    return X


X = preprocess(X, y, dims=2)
X_train, X_test, y_train, y_test = sklearn.cross_validation.train_test_split(X, y, test_size=0.40)

wke = worst_knn_ever()
wke.fit(X_train, y_train)

lolwoops = wke.predict(X_train)
got_right = np.sum(lolwoops == y_train)
score = float(got_right) / len(y_train)
print("this is 1", score)

lolwoops = wke.predict(X_test)
got_right = np.sum(lolwoops == y_test)
score = float(got_right) / len(y_test)
print("this is almost 1", score)

weights = "uniform"

for n_neighbors in range(1, 11):
    # classify_and_plot(n_neighbors, weights)
    pass


def make_dist(a):
    def expdist(arr_of_dist):
        return np.exp(-a * np.power(arr_of_dist, 2))

    return expdist


n_neighbors = 3
for weights in ("uniform", "distance",):
    pass
    # classify_and_plot(n_neighbors, weights)

for alpha in (0.1, 10, 100, 1000):
    mydist = make_dist(alpha)


    def alpha_str(**kwargs):
        return "alpha={}".format(alpha)


    mydist.__str__ = alpha_str
    # classify_and_plot(n_neighbors, mydist, ws_name="a={}".format(alfa))

ws = ['uniform', 'distance']
ws.extend([make_dist(a) for a in (0.1, 10, 100, 1000)])
parameters = {
    'weights': ws,
    'n_neighbors': list(range(1, 11))
}
knn = neighbors.KNeighborsClassifier()
clf = GridSearchCV(knn, param_grid=parameters)
clf.fit(X, y)
df = DataFrame(clf.cv_results_)
pretty_table = tabulate.tabulate(df, headers='keys', tablefmt='psql')
with open("/tmp/gridsearch", "w") as results:
    results.write(pretty_table)
classify_and_plot(4, ws="distance")
