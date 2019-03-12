import sklearn.datasets
import sklearn.model_selection


class _hack:
  def __init__(self, maker):
    self.data, self.target = maker()


def load_datasets():
  dataset_loaders = (
    (sklearn.datasets.load_breast_cancer, "binary"),
    (sklearn.datasets.load_iris, "multi-class"),
    (lambda: _hack(sklearn.datasets.make_multilabel_classification), "multi-label"),
    (sklearn.datasets.load_boston, "regression"),
  )
  for dataset_loader, dataset_name in dataset_loaders:
    dataset = dataset_loader()
    X, y = dataset.data, dataset.target
    yield sklearn.model_selection.train_test_split(X, y, random_state=31337), dataset_name
