import src.tagger.implementations
import pickle
import json
import string


class POSTaggerTester(object):
    def __init__(self, resource_dir=None):
        self._resource_dir = resource_dir
        self.w2v = src.tagger.implementations.Borg()

    def load_resources(self):
        self.w2v.load_resource(self._resource_dir)

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
        - Recall    has to be computed as the number of correctly predicted
          pos tag over the number of items in the gold standard
        - Coverage has to be computed as the number of predicted pos tag over
          the number of items in the gold standard
        - F1 has to be computed as the armonic mean between precision
          and recall (2* P * R / (P + R))
        """

        import conllu.parser
        with open(test_file_path) as fin:
            data = conllu.parser.parse(fin.read())
        sentences = [[word['form'].lower() for word in sentence] for sentence in data]
        labels = [[word['upostag'] for word in sentence] for sentence in data]
        predicted = lstm_pos_tagger.predict_mass(sentences)

        nested_sentences = sentences
        # flatten stuff
        sentences = [word for sentence in sentences for word in sentence]
        labels = [label for sent_labels in labels for label in sent_labels]

        tags = ['ADJ', 'ADP', 'ADV', 'AUX', 'CONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT',
                'SCONJ', 'SYM', 'VERB', 'X']
        occurences = {k: 0 for k in tags}
        good_guesses = {k: 0 for k in tags}
        bad_guesses = {k: 0 for k in tags}
        confusion = {k: {k: 0 for k in tags} for k in tags}

        idx = 0
        with open("pos_tagged_sentences.txt", "w") as fout:
            for current_sentence in nested_sentences:
                ys = predicted[idx:idx+len(current_sentence)]
                fout.write(" ".join(current_sentence) + "\n")
                fout.write(" ".join(ys) + "\n")

        for x, yp, yt in zip(sentences, predicted, labels):
            if x in string.punctuation:
                yp = 'PUNCT'
            if any(str.isnumeric(c) for c in x):
                yp = 'NUM'
            confusion[yp][yt] += 1
            occurences[yt] += 1
            if yp == yt:
                good_guesses[yp] += 1
            else:
                print(x, ": got", yp, "was", yt)
                bad_guesses[yp] += 1

        precision = {k: 0 for k in tags}
        recall = {k: 0 for k in tags}
        for tag in tags:
            gg = good_guesses[tag]
            bg = bad_guesses[tag]
            total = occurences[tag]
            if gg + bg == 0:
                if total == 0:
                    precision[tag] = 1
                else:
                    precision[tag] = 0
            else:
                precision[tag] = gg / (gg + bg)

            if total == 0:
                recall[tag] = 1
            else:
                recall[tag] = gg / total

        # print("precision:")
        # for p in precision: print(p, precision[p])
        # print("recall")
        # for r in recall: print(r, recall[r])

        p = sum(precision.values()) / len(precision)
        r = sum(recall.values()) / len(recall)
        results = {
            'precision': p,
            'recall': r,
            'f1': (2 * p * r) / (p + r),
            'coverage': 1.0,
        }
        with open("confusion", 'wb') as fout:
            pickle.dump(confusion, fout)
        with open("results.txt", "w") as f:
            f.write(json.dumps(results))
        return results
