import lazy_import
np = lazy_import.lazy_module("numpy")
glob = lazy_import.lazy_module("glob")
zipfile = lazy_import.lazy_module("zipfile")
sklearn = lazy_import.lazy_module("sklearn")
from io import StringIO


def load_file(f, path):
    data = f.read(path).decode('utf-8')
    return np.genfromtxt(StringIO(data), delimiter=' ')


def load_datasets(challenge_nr):
    for dataset_zip in glob.glob("datasets/{}/*.zip".format(challenge_nr)):
        dataset_name = dataset_zip.split("/")[-1][:-4]
        with zipfile.ZipFile(dataset_zip, "r") as f:
            print("\t", "loading", dataset_name)
            data = load_file(f, dataset_name + "_train.data")
            target = load_file(f, dataset_name + "_train.solution")

        print("\t", len(data), "datapoints")
        assert(len(data) == len(target))
        yield (**sklearn.model_selection.train_test_split(data, target, random_state=31337)) + dataset_name

