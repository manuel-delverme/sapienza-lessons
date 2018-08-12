import warnings

warnings.filterwarnings("ignore")

from sklearn.linear_model import RidgeClassifier
from sklearn.linear_model import Perceptron
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import NearestCentroid

RANDOM_STATE = 31337

binary_class_models = {"Ridge Classifier": (
    RidgeClassifier,
    {'tol': 1e-2, 'solver': "auto", 'random_state': RANDOM_STATE},
    ({'name': 'alpha', 'type': 'continuous', 'domain': (0., 1.)},),
), "Perceptron": (
    Perceptron,
    {'random_state': RANDOM_STATE},
    (
        {'name': 'alpha', 'type': 'continuous', 'domain': (0.00001, 0.0010)},
        {'name': 'eta0', 'type': 'continuous', 'domain': (0.1, 1.)},
    ),
), "LinearSVC+L1": (
    LinearSVC,
    {
        'random_state': RANDOM_STATE,
        'penalty': 'l1',
        'dual': False,
    }, (
        {'name': 'C', 'type': 'continuous', 'domain': (1e-5, 1e2)},
        # {'name': 'loss', 'type': 'categorical', 'domain': (0, 1)},
    ),
), "KNeighborsClassifier": (
    KNeighborsClassifier,
    {}, (
        {'name': 'n_neighbors', 'type': 'discrete', 'domain': range(1, 100)},
    ),
), "RandomForestClassifier": (
    RandomForestClassifier,
    {
        'random_state': RANDOM_STATE,
    }, (
        {'name': 'max_depth', 'type': 'discrete', 'domain': range(1, 10)},
    ),
)}
multi_class_models = binary_class_models.copy()
