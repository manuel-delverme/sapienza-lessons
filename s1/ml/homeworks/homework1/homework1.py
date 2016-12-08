import numpy as np
import random
import PIL
import sklearn.decomposition
import matplotlib.pyplot as plt
import sklearn.cross_validation
import sklearn.preprocessing


def dim_reduction(dataset, classes, plot=False):
    dims = [0, 2, 9]
    dimensions = max(dims) + 2
    transform = sklearn.decomposition.PCA(n_components=dimensions * 2)  # <- hand engineered
    print("using {} dimensions".format(dimensions))
    dataset_t = transform.fit_transform(dataset)
    if plot:
        for index, i in enumerate(dims):
            print("dimensions: {}, {}".format(i, i + 1))
            plt.title("dimensions: {}, {}".format(i, i + 1))
            plt.scatter(dataset_t[:, i], dataset_t[:, i + 1], c=classes)
            plt.show()
    dim_to_keep = []
    for dim, ratio in enumerate(transform.explained_variance_ratio_):
        print("dim", dim, np.round(ratio * 100, decimals=2), "%")
        if ratio > 0.01:
            dim_to_keep.append(dim)
    assert len(dim_to_keep) < len(dataset)  # need to keep more dims
    print("keep dimensions:", dim_to_keep)
    return dataset_t[:, :len(dim_to_keep)]


def normalize(dataset):
    dataset -= dataset.mean()
    dataset /= np.sqrt(dataset.var())
    print("updated dataset")
    print("mu = {}; sigma = {}".format(dataset.mean(), dataset.var()))
    return dataset


def load_dataset(base_path, num_classes):
    num_samples_per_class = 72
    features = 49152
    dataset = np.zeros((num_samples_per_class * num_classes, features))
    labels = []
    index = 0
    klass = 0
    for img_number in random.sample(range(100), num_classes):  # [33, 3, 16, 22]:
        for angle in range(0, 360, 5):
            img_path = "obj{}__{}.png".format(img_number, angle)
            haforgiveish = np.asarray(PIL.Image.open(base_path + img_path))
            flat_img = haforgiveish.ravel()
            dataset[index] = flat_img
            index += 1
            labels.append(klass)
        print("we loaded {} row for {}".format(index, img_path))
        klass += 1
    print("mu = {}; sigma = {}".format(dataset.mean(), dataset.var()))
    return dataset, labels


"""

def calculateProbability(x, mean, stdev):
    exponent = math.exp(-(math.pow(x-mean,2)/(2*math.pow(stdev,2))))
    return (1 / (math.sqrt(2*math.pi) * stdev)) * exponent
    ode for the calculateClassProbabilities() function

def calculateClassProbabilities(summaries, inputVector):
	probabilities = {}
	for classValue, classSummaries in summaries.iteritems():
		probabilities[classValue] = 1
		for i in range(len(classSummaries)):
			mean, stdev = classSummaries[i]
			x = inputVector[i]
			probabilities[classValue] *= calculateProbability(x, mean, stdev)
	return probabilities

def calculateClassProbabilities(summaries, inputVector):
    probabilities = {}
    for classValue, classSummaries in summaries.iteritems():
        probabilities[classValue] = 1
	for i in range(len(classSummaries)):
            mean, stdev = classSummaries[i]
            x = inputVector[i]
            probabilities[classValue] *= calculateProbability(x, mean, stdev)
    return probabilities
    """


class nbClassifier(object):
    def __init__(self):
        self.probs = None

    def train(self, dataset, labels):
        x_dims = len(dataset[0])
        num_labels = len(set(labels))
        min_value = dataset.min()
        max_value = dataset.max()
        domain_size = max_value - min_value
        offset = min_value

        probs = np.zeros((num_labels, x_dims, domain_size))
        for image, label in zip(dataset, labels):
            for pixel_num, value in enumerate(image):
                index = int(offset - value)
                probs[label][pixel_num][index] += 1
        self.probs = probs / dataset.size

    def test(self, train_set, train_labels):
        accuracy = 0
        for point, label in zip(train_set, train_labels):
            y = classifier.classify(point)
            if label == y:
                accuracy += 1
        return accuracy / len(train_labels)

    def classify(self, point):
        guesses = [1 for _ in self.probs]
        for dimension, value in enumerate(point):
            for label, probs in enumerate(self.probs):
                guesses[label] *= probs[label][dimension]
        max_prob = max(guesses)
        for label, prob in enumerate(guesses):
            print(label, prob)
            if prob == max_prob:
                guessed_label = label
        return guessed_label


if __name__ == "__main__":
    base_path = "datasets/coil-100/"
    dataset, labels = load_dataset(base_path, num_classes=4)
    dataset = normalize(dataset)
    dataset = dim_reduction(dataset, labels)
    train_set, test_set, train_labels, test_labels = sklearn.cross_validation.train_test_split(dataset, labels,
                                                                                               test_size=0.33)
    classifier = nbClassifier()
    classifier.train(dataset=train_set, labels=train_labels)
    accuracy = classifier.test(train_set, train_labels)
    print("accuracy", accuracy)
