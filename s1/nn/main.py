import pickle
import config
import data_loader
import tqdm

"""
SKIPPED:  multi-label Perceptron bad input shape (75, 5)
running classifier RandomForestClassifier
100%|██████████| 3/3 [00:03<00:00,  1.55s/it]
  0%|          | 0/4 [00:00<?, ?it/s]SKIPPED:  regression Ridge Classifier Unknown label type: (array([50. , 14.4, 22.7, 19.9, 13.9, 15. , 22.7, 13.4, 23.1, 23.6, 18.4,
       18.9, 21.9,  8.8, 12.7, 50. , 13.1, 21.2, 19.3, 22.6, 22.2, 22. ,
       19.6, 14.1, 23.4, 29. , 18.5, 13.6, 20.1,  8.5, 14.3, 20.9, 19.4,
       16.5, 35.2, 17.5, 13.8, 22.4, 18.3, 22.2, 22. , 33.2, 22.5, 50. ,
       21.2, 36.4, 23.2, 35.4, 11.9, 20.6, 12.7, 23.1, 17.6, 18.9, 13.5,
       24.7, 22.3, 43.5, 11.9, 12.1, 21.4, 13.1, 19.2, 50. , 19. , 20.2,
       18.1, 42.3, 19.7, 25.3, 23.3, 10.9, 17. , 22.8, 19.3, 21.5, 14.9,
       21.4, 32.9, 23.1, 22.8, 31.6, 15.6, 24.1, 20.6, 16.7, 21. , 15.4,
       39.8, 26.4, 50. , 23.4, 37. , 44.8, 14.4, 20.7, 21.7, 17.4, 14.9,
       10.4, 18.7, 19.9, 21.9, 23.6, 22.8, 23. , 14.6, 24.5, 17.8, 26.7,
       19.5, 23.3,  8.3, 24.8, 29.4, 16.3, 20. , 30.3, 18.6, 22.1, 18.7,
       33.1, 44. , 12.3, 13.2, 19.3, 16.2, 19.4, 23.5, 12. , 36.2, 22. ,
       18.9, 45.4, 23.7, 11.3, 25. , 23.9, 20. , 28.7, 34.7, 19.2, 32. ,
       19.4, 27.5, 17.8, 10.2, 15.1, 20.8, 17.2, 16.1, 10.8, 19.6, 21.2,
       23.8, 18.8, 19.9, 10.5, 17.2, 20.5,  5.6, 29.1, 23.7, 21.4, 19.5,
       23.1, 23.2, 46.7,  9.7, 15.6,  8.7, 34.6, 17.8, 23.9, 20. , 16.8,
       14.3, 10.9, 33.4,  5. , 32.4, 13.6, 27.5, 21.7, 20.6, 24. , 11.7,
       20. , 19.6, 20.6, 15.6, 17.8, 33.2, 18.4, 19. , 18.9, 26.6, 21. ,
       11.8, 25. , 19.5, 12.8, 17.4, 10.2, 30.1, 50. , 13.8,  7. , 16.7,
       19.1, 18.3, 22.2, 33.8, 20.3, 36.2, 23.8,  8.4, 18.7, 31.5, 23.7,
        8.3, 24.7, 24.4, 28.4, 17.9,  8.4, 31.7, 10.5, 21.5, 17.7, 23. ,
       19.4, 28. , 24.1, 19.1, 35.4, 19.7, 22.6, 17.3, 11.7, 27.9, 28.1,
       37.6, 33.3, 24.8, 14.8, 20.8, 26.6, 41.3, 28.7, 17.1, 23.1, 16.6,
       50. , 23.7, 17.5, 30.8, 24.5, 37.3, 25. , 22.2, 28.2, 37.9, 23.2,
       20.2, 16.1, 21.2, 50. , 16.2, 19.8, 18.6, 30.5, 13.5, 16.6, 22.2,
       16.5, 16.1, 20.1,  8.8, 11.8, 32. , 17.1, 20.3, 30.1,  7.5, 20.6,
       15. ,  7.2, 11. , 24.3, 20.5, 22.9, 19.4, 36.5, 13.3, 18.5, 48.3,
       28.5,  7.2, 15.6, 19.5, 17.1, 20.4, 10.4, 24.4, 18.8, 21.8, 35.1,
       19.8, 14.6, 18. , 20.8,  8.1, 29.1, 36. , 23. , 22.8, 22. , 24.4,
       48.5, 34.9, 19.6, 27.5, 25. , 27.1, 43.1, 15.4, 19.4, 15.6, 31.1,
       20.1,  7. , 33. , 18.4, 13.4, 24.1, 24.6, 23.3, 30.7,  7.2, 14.5,
       12.7, 38.7, 23.1,  6.3, 24.3, 20.4, 21.2, 19.3, 17.2, 23.3, 14.1,
       23.9, 24.8, 18.2, 16. , 23. , 19.9, 26.6, 13.3, 15.2, 23.8, 33.1,
       22.4, 34.9, 17.8, 46. , 16.4, 19.3, 21.1, 14. , 22.5, 29.6, 22.6,
       34.9, 42.8, 15.2, 14.5, 32.5]),)
SKIPPED:  regression KNeighborsClassifier Unknown label type: 'continuous'
SKIPPED:  regression Perceptron Unknown label type: (array([ 5. ,  5.6,  6.3,  7. ,  7.2,  7.5,  8.1,  8.3,  8.4,  8.5,  8.7,
        8.8,  9.7, 10.2, 10.4, 10.5, 10.8, 10.9, 11. , 11.3, 11.7, 11.8,
       11.9, 12. , 12.1, 12.3, 12.7, 12.8, 13.1, 13.2, 13.3, 13.4, 13.5,
       13.6, 13.8, 13.9, 14. , 14.1, 14.3, 14.4, 14.5, 14.6, 14.8, 14.9,
       15. , 15.1, 15.2, 15.4, 15.6, 16. , 16.1, 16.2, 16.3, 16.4, 16.5,
       16.6, 16.7, 16.8, 17. , 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7,
       17.8, 17.9, 18. , 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8,
       18.9, 19. , 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8, 19.9,
       20. , 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9, 21. ,
       21.1, 21.2, 21.4, 21.5, 21.7, 21.8, 21.9, 22. , 22.1, 22.2, 22.3,
       22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 23. , 23.1, 23.2, 23.3, 23.4,
       23.5, 23.6, 23.7, 23.8, 23.9, 24. , 24.1, 24.3, 24.4, 24.5, 24.6,
       24.7, 24.8, 25. , 25.3, 26.4, 26.6, 26.7, 27.1, 27.5, 27.9, 28. ,
       28.1, 28.2, 28.4, 28.5, 28.7, 29. , 29.1, 29.4, 29.6, 30.1, 30.3,
       30.5, 30.7, 30.8, 31.1, 31.5, 31.6, 31.7, 32. , 32.4, 32.5, 32.9,
       33. , 33.1, 33.2, 33.3, 33.4, 33.8, 34.6, 34.7, 34.9, 35.1, 35.2,
       35.4, 36. , 36.2, 36.4, 36.5, 37. , 37.3, 37.6, 37.9, 38.7, 39.8,
       41.3, 42.3, 42.8, 43.1, 43.5, 44. , 44.8, 45.4, 46. , 46.7, 48.3,
       48.5, 50. ]),)
SKIPPED:  regression RandomForestClassifier Unknown label type: 'continuous'
"""

# import warnings
# warnings.filterwarnings("ignore")
# import logging
# logging.basicConfig()
# logging.getLogger().setLevel(logging.ERROR)

import GPyOpt
import time
import sklearn
import sklearn.metrics
import estimators.models

RANDOM_STATE = 31337
DEBUG = True
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

overall_results = {}

for (X_train, X_test, y_train, y_test), dataset_name in data_loader.load_datasets():
  results = []
  for clf_name, (clf, defaults, search_space) in tqdm.tqdm(estimators.models.model_by_name[dataset_name].items()):
    print('Optimizing {} with {} parameters'.format(clf_name, ",".join(s['name'] for s in search_space)))
    if True:
    # try:
      def make_fitness(clf_class, defaults):
        def fitness_fn(suggested_values):
          suggested_values, = suggested_values

          model_parameters = defaults.copy()
          for variable, suggested_value in zip(search_space, suggested_values):
            if variable['type'] == 'discrete':
              suggested_value = int(suggested_value)
            model_parameters[variable['name']] = suggested_value

          clf_ = clf_class(**model_parameters)
          clf_.fit(X_train, y_train)
          pred = clf_.predict(X_test)

          return sklearn.metrics.accuracy_score(y_test, pred)

        return fitness_fn

      opt = GPyOpt.methods.BayesianOptimization(
          f=make_fitness(clf, defaults),  # function to optimize
          domain=search_space,  # box-constraints of the problem
          acquisition_type='EI',  # LCB acquisition
          acquisition_weight=0.3,  # Exploration exploitation
          initial_design_numdata=5,
          verbosity=False,
          maximize=True,
      )
      design_space = GPyOpt.Design_space(search_space)
      opt.run_optimization(max_iter=1 if DEBUG else 1000)  # , verbosity=31337)
      opt.plot_convergence('plots/{}_convergence.png'.format(dataset_name))
      opt.plot_acquisition('plots/{}_acquisition.png'.format(dataset_name))

      results.append((clf_name, -opt.fx_opt))
      print(clf_name, "scored", results[-1][1])
    # except Exception as e:
    #   print('SKIPPED: ', dataset_name, clf_name, e)

  sorted_results = sorted(results, key=lambda x: -x[1])
  overall_results[dataset_name] = sorted_results

with open('overall_results.pkl', 'wb') as fout:
  pickle.dump(fout, overall_results)


results = []
losses = ('squared_hinge', 'hinge')

for clf_name, (clf, defaults, search_space) in estimators.binary.items():
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

  # # Gaussian process and Bayesian optimization
  # objective = GPyOpt.core.task.SingleObjective(obj_func.f, num_cores=1)
  # model = GPyOpt.estimators.GPModel(exact_feval=False, optimize_restarts=5, verbose=False)
  # aquisition_opt = GPyOpt.optimization.AcquisitionOptimizer(feasible_space)
  # acquisition = GPyOpt.acquisitions.AcquisitionLCB(model, feasible_space, optimizer=aquisition_opt)
  # evaluator = GPyOpt.core.evaluators.Sequential(acquisition, batch_size=1)
  # BOpt = GPyOpt.methods.ModularBayesianOptimization(model, feasible_space, objective, acquisition, evaluator,
  #                                                   initial_design)

  # while queries < max_query and best_f > 0:
  #   queries += 1
  #   BOpt.run_optimization(max_iter=1)
  #   best_f = BOpt.fx_opt
  #   if queries % 5 == 0: print('Query %i, Objective Function %0.2f' % (queries, best_f))  # Print every 5th query

  # if best_f > 0:
  #   print('Attack failed.')
  # else:
  #   print('Success!')
