from sklearn.linear_model import RidgeClassifier
from sklearn.linear_model import Perceptron
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from estimators.shared import add_model

RANDOM_STATE = 31337



# ----------------------- binary estimators ----------------------
models = {}
add_model(
    models, name="Ridge Classifier", klass=RidgeClassifier, const={},
    space=({'name': 'alpha', 'type': 'continuous', 'domain': (0., 1.)}, )
)
add_model(
    models, name="Perceptron Classifier", klass=Perceptron, const={'random_state': RANDOM_STATE},
    space=(
      {'name': 'alpha', 'type': 'continuous', 'domain': (0.00001, 0.0010)},
      {'name': 'eta0', 'type': 'continuous', 'domain': (0.1, 1.)},)
)
# add_model(
#     models, name="LinearSVC", klass=LinearSVC,
#     const={'random_state': RANDOM_STATE, 'penalty': 'l1', 'dual': False, },
#     space=(
#       {'name': 'C', 'type': 'continuous', 'domain': (1e-5, 1e2)},
#       {'name': 'loss', 'type': 'categorical', 'domain': (1, 2)},
#     ))
add_model(
    models, name="KNeighbors Classifier", klass=KNeighborsClassifier, const={},
    space=(
      {'name': 'n_neighbors', 'type': 'discrete', 'domain': range(1, 75)},
    ))
add_model(
    models, name="RandomForest Classifier", klass=RandomForestClassifier, const={'random_state': RANDOM_STATE, },
    space=(
      {'name': 'max_depth', 'type': 'discrete', 'domain': range(1, 10)},
    ))
