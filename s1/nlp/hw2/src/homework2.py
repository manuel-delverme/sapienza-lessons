from abc import ABCMeta, abstractmethod
from keras.models import Sequential
from keras.models import Model
import traceback
import os
import sys


class AbstractPOSTaggerTrainer(metaclass=ABCMeta):
    def __init__(self, resource_dir=None):
        self._resource_dir = resource_dir

    @abstractmethod
    def load_resources(self):
        pass

    @abstractmethod
    def train(self, training_path):
        """
        Train the keras model from the training data.

        :param training_path: the path to training file
        :return: the keras model of type Sequential
        """
        pass


class ModelIO:
    @staticmethod
    def save(model, output_path):
        """
        Save the model to in the file pointed by the output_path variable

        :param model: the trained Sequential model
        :param output_path: the path to the file on which the model have to 
                            be saved
        :return: no return value is required
        """
        model.save(output_path)

    @staticmethod
    def load(model_file_path):
        """
        Load a sequential model saved in the file pointed by model_file_path

        :parah model_file_path: the path to the file that has to be loaded
        :return: a sequential model loaded from the file
        """
        import keras
        return keras.models.load_model(model_file_path)


class AbstractPOSTaggerTester(metaclass=ABCMeta):
    def __init__(self, resource_dir=None):
        self._resource_dir = resource_dir

    @abstractmethod
    def load_resources(self):
        pass

    @abstractmethod
    def test(self, lstm_pos_tagger, test_file_path):
        """
        Test the lstm_pos_tagger against the gold standard.

        :param lst_pos_tagger: an istance of AbstractLSTMPOSTagger that has to be tested.
        :param test_file_path: a path to the gold standard file.

        :return: a dictionary that has as keys 'precision', 'recall', 
        'coverage' and 'f1' and as associated value their respective values.

        Additional info:
        - Precision has to be computed as the number of correctly predicted 
          pos tag over the number of predicted pos tags.
        - Recall has to be computed as the number of correctly predicted 
          pos tag over the number of items in the gold standard
        - Coverage has to be computed as the number of predicted pos tag over 
          the number of items in the gold standard
        - F1 has to be computed as the armonic mean between precision 
          and recall (2* P * R / (P + R)) 
        """
        pass


class AbstractLSTMPOSTagger(metaclass=ABCMeta):
    def __init__(self, model, resource_dir=None):
        self._model = model
        self._resource_dir = resource_dir

    @abstractmethod
    def load_resources(self):
        pass

    def get_model(self):
        return self._model

    @abstractmethod
    def predict(self, sentence):
        """
        predict the pos tags for each token in the sentence.
        :param sentence: a list of tokens.
        :return: a list of pos tags (one for each input token).
        """
        pass


class Test:
    def __init__(self, training_path, model_path, gold_stanrdar_path, resource_dir):
        self._training_path = training_path
        self._model_path = model_path
        self._gold_standard_path = gold_stanrdar_path
        self._resource_dir = resource_dir

    def test(self, lstm_trainer_implementation, lstm_tester_implementation, no_train=False):

        if no_train:
            model = ModelIO.load(self._model_path)
            print('TEST 0\t\tNO-TRAIN')
        else:
            lstm_trainer_implementation.load_resources()
            model = lstm_trainer_implementation.train(self._training_path)
            assert type(model) == Sequential
            print('TEST 0\t\tPASSED')
            ModelIO.save(model, self._model_path)
            model = ModelIO.load(self._model_path)

        assert isinstance(model, Model)

        print('TEST 1\t\tPASSED')
        postagger = LSTMPOSTagger(model, self._resource_dir)
        postagger.load_resources()
        lstm_tester_implementation.load_resources()
        results = lstm_tester_implementation.test(postagger, self._gold_standard_path)
        print("results", results)
        assert type(results) == dict
        assert 'precision' in list(results.keys())
        assert 'recall' in list(results.keys())
        assert 'coverage' in list(results.keys())
        assert 'f1' in list(results.keys())

        print('TEST 2\t\tPASSED')

        test_sentence = ['this', 'is', 'an', 'easy', 'test', '.']
        prediction = postagger.predict(test_sentence)[0]
        print("predicted", prediction)
        assert prediction == ['PRON', 'VERB', 'DET', 'ADJ', 'NOUN', 'PUNCT']

        print('TEST 3\t\tPASSED')

        return results


if __name__ == '__main__':
    """
    Main to run the test of the homework 2.
    Use the parameter --no-train in order to skip the training of the model
    @@@@@@@@@@@@@@@@@@ WARNING!!! @@@@@@@@@@@@@@@@@@@@
    the program will not check if model_path already exist and will overwrite it if it
    is the case
    """
    if len(sys.argv) < 3:
        print('usage: python', sys.argv[0], '[--no-train] model_path, homework_dir[, resource_dir]')
        sys.exit(-1)
    model_index = 1
    homework_dir_index = 2
    resource_dir_index = 3
    no_train = False
    if '--no-train' in sys.argv:
        model_index = 2
        homework_dir_index = 3
        resource_dir_index = 4
        no_train = True

    model_output_path = sys.argv[model_index]
    print('model_output_path', model_output_path)
    homework_dir = sys.argv[homework_dir_index]
    print('homework_dir:', homework_dir)
    resource_dir = None
    if len(sys.argv) > resource_dir_index:
        resource_dir = sys.argv[resource_dir_index]
    src_dir = homework_dir + 'src/'
    if not os.path.exists(src_dir):
        raise IOError('src/ folder not found in ' + homework_dir)
    data_dir = homework_dir + 'data/'
    if not os.path.exists(data_dir):
        raise IOError('data/ folder not found in ' + homework_dir)

    print('')
    print('model output:', model_output_path)
    print('homework dir:', homework_dir)
    print('src dir:', src_dir)
    print('data dir:', data_dir)
    print('resource dir:', 'NONE' if resource_dir == None else resource_dir)
    print('')

    # dynamic import of modules
    sys.path.append(src_dir)
    from src.tagger.POSTaggerTester import POSTaggerTester
    from src.tagger.POSTaggerTrainer import POSTaggerTrainer
    from src.tagger.LSTMPOSTagger import LSTMPOSTagger

    ## get files
    training_data = data_dir + 'en-ud-train.conllu'
    test_data = data_dir + 'en-ud-test.conllu'

    if not os.path.exists(training_data):
        raise IOError('en-ud-train.conllu not found in ' + data_dir)

    if not os.path.exists(test_data):
        raise IOError('en-ud-test.conllu not found in ' + data_dir)

    test = Test(training_data, model_output_path, test_data, resource_dir)

    trainer = POSTaggerTrainer(resource_dir)
    tester = POSTaggerTester(resource_dir)

    name = ''
    if homework_dir.endswith('/'):
        name = homework_dir[:-1]
    else:
        name = homework_dir

    name = name[name.rfind("/"):]

    try:
        results = test.test(trainer, tester, no_train=no_train)
        print(name, "PASSED")
    except Exception as e:
        print(name, "FAILED")
        raise traceback.print_exc(e)
