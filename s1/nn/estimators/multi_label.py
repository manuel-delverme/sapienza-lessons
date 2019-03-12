# import sklearn
# from sklearn.linear_model import RidgeClassifier
# from sklearn.linear_model import Perceptron
# from sklearn.svm import LinearSVC
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.ensemble import RandomForestClassifier
import config
from estimators.shared import add_model
import sklearn.multiclass

import estimators.binary

models = estimators.binary.models.copy()
# del models['Ridge Classifier']

for clf_name in ('Ridge Classifier', 'Perceptron Classifier'):
  clf, defaults, search_space = models[clf_name]
  models[clf_name] = lambda **p: sklearn.multiclass.OneVsRestClassifier(clf(**p)), defaults, search_space

# add_model(multi_label, klass=sklearn.tree.DecisionTreeClassifier, name="DecisionTreeClassifier", const={}, space=({ }))
# add_model(multi_label, klass=sklearn.tree.ExtraTreeClassifier, name="ExtraTreeClassifier", const={}, space=({ }))
# add_model(multi_label, klass=sklearn.ensemble.ExtraTreesClassifier, name="ExtraTreesClassifier", const={}, space=({ }))
# add_model(multi_label, klass=sklearn.neighbors.KNeighborsClassifier, name="KNeighborsClassifier", const={}, space=({ }))
# add_model(multi_label, klass=sklearn.neural_network.MLPClassifier, name="MLPClassifier", const={}, space=({ }))
# add_model(multi_label, klass=sklearn.neighbors.RadiusNeighborsClassifier, name="RadiusNeighborsClassifier", const={}, space=({ }))
# add_model(multi_label, klass=sklearn.ensemble.RandomForestClassifier, name="RandomForestClassifier", const={},
#           space=(
#             {'name': 'n_estimators', 'type': 'discrete', 'domain': range(10, 100)},
#             {'name': 'max_depth', 'type': 'discrete', 'domain': range(3, 10)},
#           ))
# add_model(multi_label, klass=sklearn.linear_model.RidgeClassifierCV, name="RidgeClassifierCV", const={},
#           space=({'name': 'alpha', 'type': 'continuous', 'domain': (0., 1.)})
#           )
