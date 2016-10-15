import numpy as np
import random
from PIL import Image
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt      
from itertools import permutations


base_path = "/home/noflip/Documents/sapienza/s1/ml/dataset/coil-100/" 
plot = False

X = np.zeros((72*4, 49152))
Y = []
index = 0
klass = 0
for img_number in random.sample(range(100), 4): # [33, 3, 16, 22]:
    for angle in range(0, 360, 5):
        img_path = "obj{}__{}.png".format(img_number, angle)
        haforgiveish = np.asarray(Image.open(base_path + img_path))
        flat_img = haforgiveish.ravel()
        X[index] = flat_img
        index += 1
        Y.append(klass)
    print("we loaded {} row for {}".format(index, img_path))
    klass += 1
print("mu = {}; sigma = {}".format(X.mean(), X.var()))
X -= X.mean()
X /= np.sqrt(X.var())
print("updated X")
print("mu = {}; sigma = {}".format(X.mean(), X.var()))

dims = [0, 2, 9]
dimensions = max(dims) + 2
transform = PCA(n_components=dimensions)
print("using {} dimensions".format(dimensions))
Xt = transform.fit_transform(X)
if plot:
    for index, i in enumerate(dims):
        print("dimensions: {}, {}".format(i, i+1))
        plt.title("dimensions: {}, {}".format(i, i+1))
        plt.scatter(Xt[:, i], Xt[:, i+1], c=Y)
        plt.show()

for dim, ratio in enumerate(transform.explained_variance_ratio_):
    print("dim", dim, np.round(ratio * 100, decimals=2), "%")
    if ratio > 0.02:
        print("keep")
    else:
        print("drop")

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
