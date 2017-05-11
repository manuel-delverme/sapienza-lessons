import src.tagger.implementations
import numpy as np


class LSTMPOSTagger:
    def __init__(self, model, resource_dir=None):
        self._model = model
        self._resource_dir = resource_dir
        self.w2v = src.tagger.implementations.Borg()

    def load_resources(self):
        self.w2v.load_resource(self._resource_dir)

    def get_model(self):
        return self._model

    def predict_mass(self, sentences):
        """
        predict the pos tags for each token in the sentence.
        :param sentence: a list of lists of tokens.
        :return: a list of pos tags (one for each input token).
        """
        print("predict_mass", len(sentences))
        model = self.get_model()
        xs = []
        for sentence in sentences:
            sentences_vectors = [src.tagger.implementations.to_vector(self.w2v, word) for word in sentence]
            words_and_contexts = src.tagger.implementations.add_context_single(sentences_vectors, padding=self.w2v['padding'])
            xs.extend([word_and_context for word_and_context in words_and_contexts])
        xs = np.array(xs)
        print("sending an array of:", xs.shape)
        predictions = model.predict(xs)
        ys = src.tagger.implementations.to_tag(predictions)
        return ys

    def predict(self, sentence):
        """
        predict the pos tags for each token in the sentence.
        :param sentence: a list of tokens.
        :return: a list of pos tags (one for each input token).
        """
        model = self.get_model()
        ys = []
        sentences_vectors = [src.tagger.implementations.to_vector(self.w2v, word) for word in sentence]
        words_and_contexts = src.tagger.implementations.add_context_single(sentences_vectors, padding=self.w2v['padding'])
        xs = np.array([np.array(word_and_context) for word_and_context in words_and_contexts])
        predictions = model.predict(xs)
        ys.append(src.tagger.implementations.to_tag(predictions))
        return ys
