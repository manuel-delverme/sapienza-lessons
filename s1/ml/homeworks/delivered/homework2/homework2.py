import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# x_train = np.sort(np.random.random(150)*5)
# x_test = np.sort(np.random.random(50)*5)
#
X_test = np.load("regression_Xtest.npy").reshape(-1, 1)
X_train = np.load("regression_Xtrain.npy").reshape(-1, 1)

Y_train = np.load("regression_ytrain.npy").reshape(-1, 1)
Y_test = np.load("regression_ytest.npy").reshape(-1, 1)

# def true_function(x):
#     return 3 + 0*x + 2*x**2 - x**3 + 4*x**4

# y_train = true_function(x_train) + np.sort(np.random.random(150)*5000)
# y_test = true_function(x_test) + np.sort(np.random.random(50)*5000)

# y_avg = np.average(y_train)
# plt.scatter(x_train, y_train)
# plt.plot(x_train, [y_avg] * len(y_train), 'b-')

# b = y_train - y_avg
# b = y_train - y_avg
# plt.scatter(x_train, y_train - y_avg)


# plt.plot(X_train, Y_train)
# lr = LinearRegression()
# lr.fit(X_train, Y_train)
# Y_predicted = lr.predict(X_test)
plt.title("test data vs train data")
plt.scatter(X_test, Y_test, c='r')
plt.scatter(X_train, Y_train, c='b')

# delta = (Y_predicted - Y_test)
# mse = np.dot(delta.transpose(), delta) / delta.shape[0]
# print(mse)
plt.show()

mses = []
MAX_DEGREE = 10
plot = False
for degree in range(1, MAX_DEGREE + 1):
    print("using degree = {}".format(degree))
    transform = PolynomialFeatures(degree=degree, include_bias=False)
    X_train_poly = transform.fit_transform(X_train)

    lr = LinearRegression()
    fitter = lr.fit(X_train_poly, Y_train)

    graph_xs = np.linspace(-1, 5.5, 100).reshape(-1, 1)
    graph_poly_xs = transform.fit_transform(graph_xs) # this is poly space (?)
    graph_ys = fitter.predict(graph_poly_xs)

    if plot:
        # plot the fitted line
        plt.plot(graph_xs, graph_ys)

        # plot the real values
        plt.scatter(X_test, Y_test, c='r')

    # transform the test set
    X_test_poly = transform.fit_transform(X_test)
    Y_predicted = fitter.predict(X_test_poly)
    delta = (Y_predicted - Y_test)
    # print(delta)
    mse = np.dot(delta.transpose(), delta) / len(delta)
    # print(mse[0][0])
    mses.append(mse[0][0])

    # X_train_poly = transform.fit_transform(X_train)
    Y_predicted = fitter.predict(X_train_poly)
    delta = (Y_predicted - Y_test)
    mse = np.dot(delta.transpose(), delta) / len(delta)
    print("train error", mse[0][0])

    if plot:
        plt.show()

plt.plot(range(1, MAX_DEGREE-1), mses)
plt.show()
