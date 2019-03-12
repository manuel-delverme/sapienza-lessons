import sklearn.ensemble
import sklearn.neural_network
import sklearn.linear_model
import sklearn.neighbors

import estimators.binary
models = estimators.binary.models.copy()

_, defaults, search_space = models['RandomForest']
models['RandomForest'] = (sklearn.ensemble.RandomForestRegressor, defaults, search_space)

_, defaults, search_space = models['Perceptron']
models['Perceptron']
models['SGDRegressor'] = (sklearn.linear_model.SGDRegressor, defaults, search_space)

_, defaults, search_space = models['Ridge']
models['Ridge'] = (sklearn.linear_model.Ridge, defaults, search_space)

_, defaults, search_space = models['KNeighbors']
models['KNeighbors'] = (sklearn.neighbors.KNeighborsRegressor, defaults, search_space)
