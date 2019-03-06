# import GPy
import lazy_import
import warnings
import data_loader
import tqdm
warnings.filterwarnings("ignore")
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

zipfile = lazy_import.lazy_module("zipfile")
glob = lazy_import.lazy_module("glob")
GPyOpt = lazy_import.lazy_module("GPyOpt")
time = lazy_import.lazy_module("time")
np = lazy_import.lazy_module("numpy")
sklearn = lazy_import.lazy_module("sklearn")
sklearn.metrics = lazy_import.lazy_module("sklearn.metrics")
sklearn.model_selection = lazy_import.lazy_module("sklearn.model_selection")
models = lazy_import.lazy_module("models")

RANDOM_STATE = 31337
losses = ('squared_hinge', 'hinge')

print(" ________________________")
print("<# 1-binary-classification/>")
print(" ------------------------")
print("        \   ^__^")
print("         \  (oo)\_______")
print("            (__)\       )\\/\\")
print("                ||----w |")
print("                ||     ||")
print("\n" * 2)
print("=" * 20, "optim", "=" * 20)

for challenge_nr in range(1, 5):
    overall_results = []
    for X_train, X_test, y_train, y_test, dataset_name in data_loader.load_datasets(challenge_nr=1):
        results = []
        for clf_name, (clf, defaults, search_space) in tqdm.tqdm(models.binary_class_models.items()):
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
                    clf_.fit(X_train, y_train)
                    pred = clf_.predict(X_test)

                    score = sklearn.metrics.accuracy_score(y_test, pred)
                    return -score
                return fitness

            opt = GPyOpt.methods.BayesianOptimization(
                f=make_fitness(clf, defaults),  # function to optimize
                domain=search_space,  # box-constraints of the problem
                acquisition_type='MPI',  # LCB acquisition
                acquisition_weight=0.3,  # Exploration exploitation
                initial_design_numdata=5,
                verbosity=False,
            )
            design_space = GPyOpt.Design_space(search_space)
            opt.run_optimization(max_iter=1)  # , verbosity=31337)
            results.append((clf_name, opt.fx_opt))

        print("=" * 20, "results", "=" * 20)
        print("\n" * 1)
        sorted_results = sorted(results, key=lambda x: -x[1])
        for k, v in sorted_results:
            print(k, v)
        print("=" * 20, "results", "=" * 20)
        overall_results.append(dataset_name, sorted_results[0])

    print("=" * 20, "results", "=" * 20)
    print("=" * 20, "results", "=" * 20)
    print(overall_results)
    print("=" * 20, "results", "=" * 20)
    print("=" * 20, "results", "=" * 20)
