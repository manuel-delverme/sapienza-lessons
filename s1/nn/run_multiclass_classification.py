# import GPy
import warnings

warnings.filterwarnings("ignore")

import GPyOpt
import time
import numpy as np
import sklearn.metrics
from sklearn.utils.extmath import density
import estimators
import sklearn.linear_model

RANDOM_STATE = 31337

# human way
# lets plot a matrix for paramters comparison and correlation checking:
print("=" * 20, "optim", "=" * 20)
print("\n" * 2)
print("________________________")
print("<# 2-multiclass-classification/>")
print(" ------------------------")
print("        \   ^__^")
print("         \  (oo)\_______")
print("            (__)\       )\\/\\")
print("                ||----w |")
print("                ||     ||")
print("\n" * 2)
print("=" * 20, "optim", "=" * 20)


# Lets now load the data-set in python
def load_dataset():
    import sklearn.model_selection
    from sklearn.datasets import load_iris
    data = load_iris()
    return sklearn.model_selection.train_test_split(data.data, data.target, random_state=31337)


X_train, X_test, y_train, y_test = load_dataset()

regression_models = [
    sklearn.linear_model.LinearRegression(),
]

results = []
losses = ('squared_hinge', 'hinge')

for clf_name, (clf, defaults, search_space) in estimators.multi_class_models.items():
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
            # print(hyper_params, "====>", score)
            return -score

        return fitness


    opt = GPyOpt.methods.BayesianOptimization(
        f=make_fitness(clf, defaults),  # function to optimize
        domain=search_space,  # box-constraints of the problem
        acquisition_type='MPI',  # LCB acquisition
        acquisition_weight=0.3,  # Exploration exploitation
        # acquisition_optimizer_type = 'CMA',
    )
    design_space = GPyOpt.Design_space(search_space)
    opt.run_optimization(max_iter=1)  # , verbosity=31337)
    # opt.plot_convergence()

    for k, v in zip(search_space, opt.x_opt):
        print(k['name'], ":=", v, end=' ')
    print("scored:", opt.fx_opt)

    results.append((clf_name, opt.fx_opt))

print("*" * 20, "results", "*" * 20)
for k, v in sorted(results, key=lambda x: -x[1]):
    print(k, v)
print("*" * 20, "results", "*" * 20)
# 3-multiclass-multilabel-sparse-class/
# 4-everything-plus-regression/
