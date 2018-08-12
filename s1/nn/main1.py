# import GPy
import zipfile
import warnings

warnings.filterwarnings("ignore")

import GPyOpt
import time
import numpy as np
import sklearn.metrics
from sklearn.utils.extmath import density
import models
import sklearn.linear_model

RANDOM_STATE = 31337

# human way
# lets plot a matrix for paramters comparison and correlation checking:
print("=" * 20, "optim", "=" * 20)
print("\n" * 2)
print("________________________")
print("<# 1-binary-classification/>")
print(" ------------------------")
print("        \   ^__^")
print("         \  (oo)\_______")
print("            (__)\       )\\/\\")
print("                ||----w |")
print("                ||     ||")
print("\n" * 2)
print("=" * 20, "optim", "=" * 20)


def load_datasets(challenge_nr):
    import ipdb; ipdb.set_trace()
    for dataset_zip in glob.glob("datasets/{}/*".format(challenge_nr)):
        dataset_name = dataset_zip.split("/")[-1][:-3]
        with zipfile.ZipFile(dataset_zip, "r") as f:
            data = f.read(dataset_name + "_train.data")
            targets = f.read(dataset_name + "_train.solution")
    return sklearn.model_selection.train_test_split(data, target, random_state=31337)

for X_train, X_test, y_train, y_test in load_datasets(challenge_nr):

results = []
losses = ('squared_hinge', 'hinge')

for clf_name, (clf, defaults, search_space) in models.binary_class_models.items():
    print("running classifier", clf_name)

    def make_fitness(clf_class, defaults):
        def fitness(hyper_params):
            hyper_params, = hyper_params
            params = defaults
            for space, param_value in zip(search_space, hyper_params):
                if space['type'] == 'discrete':
                    param_value = int(param_value)
                if space['name'] == 'loss':
                    param_value = losses[int(param_value)]
                params[space['name']] = param_value

            clf_ = clf_class(**params)

            t0 = time.time()
            clf_.fit(X_train, y_train)
            train_time = time.time() - t0

            t0 = time.time()
            pred = clf_.predict(X_test)
            test_time = time.time() - t0

            score = sklearn.metrics.accuracy_score(y_test, pred)
            return -score
        return fitness

    opt = GPyOpt.methods.BayesianOptimization(
        f=make_fitness(clf, defaults),  # function to optimize
        domain=search_space,  # box-constraints of the problem
        acquisition_type='MPI',  # LCB acquisition
        acquisition_weight=0.3,  # Exploration exploitation
    )
    design_space = GPyOpt.Design_space(search_space)
    opt.run_optimization(max_iter=1)  # , verbosity=31337)

    # for k, v in zip(search_space, opt.x_opt):
    #     print(k['name'], ":=", v, end=' ')
    # print("scored:", opt.fx_opt)
    results.append((clf_name, opt.fx_opt))

print("=" * 20, "results", "=" * 20)
print("\n" * 1)
for k, v in sorted(results, key=lambda x: -x[1]):
    print(k, v)
print("=" * 20, "results", "=" * 20)
