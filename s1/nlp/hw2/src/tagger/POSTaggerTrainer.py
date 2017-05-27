import src.tagger.implementations

class POSTaggerTrainer:
    def __init__(self, resource_dir):
        self._resource_dir = resource_dir
        self.w2v = src.tagger.implementations.Borg()

    def load_resources(self):
        self.w2v.load_resource(self._resource_dir)

    def train(self, training_path):
        """
        Train the keras model from the training data.

        :param training_path: the path to training file
        :return: the keras model of type Sequential
        """
        '''Trains a LSTM on the IMDB sentiment classification task.
        The dataset is actually too small for LSTM to be of any advantage
        compared to simpler, much faster methods such as TF-IDF + LogReg.
        Notes:
        - RNNs are tricky. Choice of batch size is important,
        choice of loss and optimizer is critical, etc.
        Some configurations won't converge.
        - LSTM loss decrease patterns during training can be quite different
        from what you see with CNNs/MLPs/etc.
        '''

        model = src.tagger.implementations.train(training_path)
        return model

