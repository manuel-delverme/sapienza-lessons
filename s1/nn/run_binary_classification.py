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

def load_datasets(challenge_nr):
    for dataset_zip in glob.glob("datasets/{}/*.zip".format(challenge_nr)):
        dataset_name = dataset_zip.split("/")[-1][:-4]
        with zipfile.ZipFile(dataset_zip, "r") as f:
            print("\t", "loading", dataset_name)
            train_file_name = dataset_name + "_train.data"
            data = f.read(dataset_name + "_train.data").decode('utf-8')
            # data = np.genfromtxt(train_file_name, delimiter=' ')

            test_file_name = dataset_name + "_train.solution"
            target = (f.read(dataset_name + "_train.solution")).decode('utf-8')
            target = [int(d) for d in target.split("\n")[:-1]]
            # target = np.genfromtxt(test_file_name, delimiter=' ')
            print("dataset\n", f.read(dataset_name + "_public.info").decode('utf-8'))

        print("\t", len(data), datapoints)
        assert (len(data) == len(target))
        yield sklearn.model_selection.train_test_split(data, target, random_state=31337)


for X_train, X_test, y_train, y_test in load_datasets(challenge_nr=1):
    results = []
    losses = ('squared_hinge', 'hinge')

    for clf_name, (clf, defaults, search_space) in models.binary_class_models.items():
        print("running classifier", clf_name)


        def make_fitness(clf_class, defaults):
            def fitness(hyper_params):
                # import ipdb; ipdb.set_trace()
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
            initial_design_numdata=5,
        )
        design_space = GPyOpt.Design_space(search_space)
        opt.run_optimization(max_iter=1)  # , verbosity=31337)

        # for k, v in zip(search_space, opt.x_opt):
        #     print(k['name'], ":=", v, end=' ')
        # print("scored:", opt.fx_opt)
        results.append((clf_name, opt.fx_opt))

    print("=" * 20, "results", "=" * 20)
    print("=" * 20, "results", "=" * 20)
    print(overall_results)
    print("=" * 20, "results", "=" * 20)
    print("=" * 20, "results", "=" * 20)
