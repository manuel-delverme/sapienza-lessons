import numpy as np
import matplotlib.pyplot as plt
import sklearn.datasets
import sklearn.preprocessing
import sklearn.decomposition
import sklearn.cluster
import sklearn.mixture


digits = sklearn.datasets.load_digits(n_class=5)
print(digits.data.shape)
data = sklearn.preprocessing.scale(digits.data)

# TODO: get only 0,1,2,3,4
n_samples, n_features = data.shape

n_digits = len(np.unique(digits.target))
labels = digits.target

print("n_digits: %d, \t n_samples %d, \t n_features %d" % (n_digits, n_samples, n_features))
print("classes", np.unique(digits.target))
pca = sklearn.decomposition.PCA(n_components=2)
reduced_data = pca.fit_transform(data)

def plot_stuff(reduced_data, model, n_classes):
    model.fit(reduced_data)
    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
    y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))


    # Obtain labels for each point in mesh. Use last trained model.
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')

    plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    try:
        centroids = model.cluster_centers_
    except Exception:
        centroids = model.means_
    plt.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=169, linewidths=3,
                color='w', zorder=10)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.title("classes: {}, model: {}".format(n_classes, repr(model)))
    plt.show()


def purity_score(clusters, classes):
    """
    Calculate the purity score for the given cluster assignments and ground truth classes

    :param clusters: the cluster assignments array
    :type clusters: numpy.array

    :param classes: the ground truth classes
    :type classes: numpy.array

    :returns: the purity score
    :rtype: float
    """

    A = np.c_[(clusters,classes)]

    n_accurate = 0.

    for j in np.unique(A[:,0]):
        z = A[A[:,0] == j, 1]
        x = np.argmax(np.bincount(z))
        n_accurate += len(z[z == x])

    return n_accurate / A.shape[0]

for n_classes in ([5] + range(3,11)):
    pass
    # kmeans = sklearn.cluster.KMeans(init='k-means++', n_clusters=n_classes, n_init=10)
    # plot_stuff(reduced_data, kmeans, n_classes)

for n_classes in range(2,11):
    gmm = sklearn.mixture.GMM(n_components=n_classes)
    plot_stuff(reduced_data, gmm, n_classes)

    k
