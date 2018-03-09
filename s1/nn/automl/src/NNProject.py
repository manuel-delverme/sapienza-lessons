# coding: utf-8
import pickle
import autosklearn.classification
import sklearn.model_selection
import sklearn.metrics

import numpy as np
import matplotlib.pyplot as plt
from scipy import io
from scipy import stats
import pickle

# Import function to get the covariate matrix that includes spike history from previous bins
from preprocessing_funcs import get_spikes_with_history

# I mport metrics
from metrics import get_R2
from metrics import get_rho

# Im port decoder functions
from decoders import WienerCascadeDecoder
from decoders import WienerFilterDecoder
from decoders import DenseNNDecoder
from decoders import SimpleRNNDecoder
from decoders import GRUDecoder
from decoders import LSTMDecoder
from decoders import XGBoostDecoder
from decoders import SVRDecoder

# optimization
# import GPy
# import GPyOpt

import numpy as np
from scipy import io
from preprocessing_funcs import bin_spikes
from preprocessing_funcs import bin_output
from utils import disk_cache


@disk_cache
def load_data():
    folder = './'
    data = io.loadmat(folder + 's1_data_raw.mat')
    spike_times = data['spike_times']  # Load spike times of all neurons
    vels = data['vels']  # Load x and y velocities
    vel_times = data['vel_times']  # Load times at which velocities were recorded
    dt = .05  # Size of time bins (in seconds)
    t_start = vel_times[0]  # Time to start extracting data - here the first time velocity was recorded
    t_end = vel_times[-1]  # Time to finish extracting data - here the last time velocity was recorded
    downsample_factor = 1  # Downsampling of output (to make binning go faster). 1 means no downsampling.

    # When loading the Matlab cell "spike_times", Python puts it in a format with an extra unnecessary dimension
    # First, we will put spike_times in a cleaner format: an array of arrays
    spike_times = np.squeeze(spike_times)
    for i in range(spike_times.shape[0]):
        spike_times[i] = np.squeeze(spike_times[i])

    ###Preprocessing to put spikes and output in bins###

    # Bin neural data using "bin_spikes" function
    neural_data = bin_spikes(spike_times, dt, t_start, t_end)

    # Bin output (velocity) data using "bin_output" function
    vels_binned = bin_output(vels, vel_times, dt, t_start, t_end, downsample_factor)

    return neural_data, vels_binned


def load_toy_data():
    X, y = sklearn.datasets.load_iris(return_X_y=True)


def preprocess_data(neural_data, vels_binned):
    bins_before = 6  # How many bins of neural data prior to the output are used for decoding
    bins_current = 1  # Whether to use concurrent time bin of neural data
    bins_after = 6  # How many bins of neural data after the output are used for decoding

    #### Format Input Covariates

    # Format for recurrent neural networks (SimpleRNN, GRU, LSTM)
    # Function to get the covariate matrix that includes spike history from previous bins
    X = get_spikes_with_history(neural_data, bins_before, bins_after, bins_current)

    # Format for Wiener Filter, Wiener Cascade, XGBoost, and Dense Neural Network
    # Put in "flat" format, so each "neuron / time" is a single feature
    X_flat = X.reshape(X.shape[0], (X.shape[1] * X.shape[2]))

    #### Format Output Covariates
    # Set decoding output
    y = vels_binned

    # Set what part of data should be part of the training/testing/validation sets
    training_range = [0, 0.7]
    testing_range = [0.7, 0.85]
    valid_range = [0.85, 1]

    # split data
    num_examples = X.shape[0]

    # Note that each range has a buffer of"bins_before" bins at the beginning, and "bins_after" bins at the end
    # This makes it so that the different sets don't include overlapping neural data
    training_set = np.arange(np.int(np.round(training_range[0] * num_examples)) + bins_before,
                             np.int(np.round(training_range[1] * num_examples)) - bins_after)
    testing_set = np.arange(np.int(np.round(testing_range[0] * num_examples)) + bins_before,
                            np.int(np.round(testing_range[1] * num_examples)) - bins_after)
    valid_set = np.arange(np.int(np.round(valid_range[0] * num_examples)) + bins_before,
                          np.int(np.round(valid_range[1] * num_examples)) - bins_after)

    # Get training data
    X_train = X[training_set, :, :]
    X_flat_train = X_flat[training_set, :]
    y_train = y[training_set, :]

    # Get testing data
    X_test = X[testing_set, :, :]
    X_flat_test = X_flat[testing_set, :]
    y_test = y[testing_set, :]

    # Get validation data
    X_valid = X[valid_set, :, :]
    X_flat_valid = X_flat[valid_set, :]
    y_valid = y[valid_set, :]

    # 3D. Process Covariates
    # We normalize (z_score) the inputs and zero-center the outputs. Parameters for z-scoring (mean/std.) should be determined on the training set only, and then these z-scoring parameters are also used on the testing and validation sets.

    # Z-score "X" inputs.
    X_train_mean = np.nanmean(X_train, axis=0)
    X_train_std = np.nanstd(X_train, axis=0)
    X_train = (X_train - X_train_mean) / X_train_std
    X_test = (X_test - X_train_mean) / X_train_std
    X_valid = (X_valid - X_train_mean) / X_train_std

    # Z-score "X_flat" inputs.
    X_flat_train_mean = np.nanmean(X_flat_train, axis=0)
    X_flat_train_std = np.nanstd(X_flat_train, axis=0)
    X_flat_train = (X_flat_train - X_flat_train_mean) / X_flat_train_std
    X_flat_test = (X_flat_test - X_flat_train_mean) / X_flat_train_std
    X_flat_valid = (X_flat_valid - X_flat_train_mean) / X_flat_train_std

    # Zero-center outputs
    y_train_mean = np.mean(y_train, axis=0)
    y_train = y_train - y_train_mean
    y_test = y_test - y_train_mean
    y_valid = y_valid - y_train_mean
    return X_flat_train, y_train, X_flat_valid, y_valid


# Neural data should be a matrix of size "number of time bins" x "number of neurons",
#  where each entry is the firing rate of a given neuron in a given time bin
# The output you are decoding should be a matrix of size "number of time bins" x "number of features you are decoding"

neural_data, vels_binned = load_data()
X_flat_train, y_train, X_flat_valid, y_valid = preprocess_data(neural_data, vels_binned)

@disk_cache
def score_wf(X_flat_train, y_train, ):
    print("#Declare model")
    model_wf = WienerFilterDecoder()

    print("#Fit model")
    model_wf.fit(X_flat_train, y_train)

    print("#Get predictions")
    y_valid_predicted_wf = model_wf.predict(X_flat_valid)

    print("#Get metric of fit")
    R2s_wf = get_R2(y_valid, y_valid_predicted_wf)
    return R2s_wf

R2s_wf = score_wf()
print('R2s:', R2s_wf)

@disk_cache
def train_automl(X_flat_train, y_train):
    model = autosklearn.classification.AutoSklearnClassifier()
    model.fit(X_flat_train, y_train)
    return model


model = train_automl(X_flat_train, y_train)
y_hat = model.predict(X_flat_valid)
print("Accuracy score", sklearn.metrics.accuracy_score(y_valid, y_hat))

