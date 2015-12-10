from __future__ import print_function

import re
import os
import sys
try:
    import cPickle as pickle
except:
    import pickle
from functools import reduce

__version__ = "0.0.4"


class Model(object):
    """Save & Load the model in/from the file system using Python's pickle
    module."""
    DEFAULT_DATA_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "model.dat")

    def __init__(self, file_path=None, new=False):
        if new:
            self.file_path = file_path if file_path else os.path.join(
                os.getcwd(), "model.dat")
        else:
            self.file_path = file_path if file_path else self.DEFAULT_DATA_PATH
        self.load(file_path)

    def load(self, file_path=None):
        """Load the serialized file from the specified file_path, and return
        the ``spam_count_total``, ``ham_count_total`` and ``token_table``. """
        file_path = file_path if file_path else self.DEFAULT_DATA_PATH
        if not os.path.exists(file_path):
            with open(file_path, 'a'):
                os.utime(file_path, None)
        with open(file_path, 'rb') as f:
            try:
                self.spam_count_total, self.ham_count_total, self.token_table = pickle.load(
                    f)
            except:
                self.spam_count_total = 0
                self.ham_count_total = 0
                self.token_table = {}

    def save(self):
        """Serialize the model using Python's pickle module, and save the
        serialized modle as a file which is indicated by ``self.file_path``."""
        with open(self.file_path, 'wb') as f:
            pickle.dump(
                (self.spam_count_total, self.ham_count_total,
                 self.token_table), f, -1)


class Detector(object):

    TOKENS_RE = re.compile(r"\$?\d*(?:[.,]\d+)+|\w+-\w+|\w+", re.U)

    def __init__(self, path=None, new=False):
        self.model = Model(path, new) if path else Model()
        self.init_rating = 0.4

    def _get_words_list(self, msg):
        return filter(lambda s: len(s) > 2,
                      self.TOKENS_RE.findall(msg.lower()))

    def save(self):
        self.model.save()

    def train(self, msg, is_spam):
        token_list = self.model.token_table
        if is_spam:
            self.model.spam_count_total += 1
        else:
            self.model.ham_count_total += 1

        for word in self._get_words_list(msg.lower()):
            if word in token_list:
                token = token_list[word]
                if is_spam:
                    token[1] += 1
                else:
                    token[0] += 1
            else:
                token_list[word] = [0, 1] if is_spam else [1, 0]

    def score(self, msg):
        """Calculate and return the spam score of a msg. The higher the score,
        the stronger the liklihood that the msg is a spam is."""
        token_table = self.model.token_table
        hashes = self._get_words_list(msg.lower())
        ratings = []
        for h in hashes:
            if h in token_table:
                ham_count, spam_count = token_table[h]
                if spam_count > 0 and ham_count == 0:
                    rating = 0.99
                elif spam_count == 0 and ham_count > 0:
                    rating = 0.01
                elif self.model.spam_count_total > 0 and self.model.ham_count_total > 0:
                    ham_prob = float(ham_count) / float(
                        self.model.ham_count_total)
                    spam_prob = float(spam_count) / float(
                        self.model.spam_count_total)
                    rating = spam_prob / (ham_prob + spam_prob)
                    if rating < 0.01:
                        rating = 0.01
                else:
                    rating = self.init_rating
            else:
                rating = self.init_rating
            ratings.append(rating)

        if (len(ratings) > 20):
            ratings.sort()
            ratings = ratings[:10] + ratings[-10:]

        product = reduce(lambda x, y: x * y, ratings)
        alt_product = reduce(lambda x, y: x * y, map(lambda r: 1.0 - r,
                                                     ratings))

        return product / (product + alt_product)

    def is_spam(self, msg):
        return self.score(msg) > 0.9


module = sys.modules[__name__]


def score(msg):
    if hasattr(module, 'obj'):
        detector = getattr(module, 'obj')
        return detector.score(msg)
    else:
        detector = Detector()
        return detector.score(msg)


def is_spam(msg):
    return score(msg) > 0.9


if __name__ == "__main__":
    d = Detector()

    d.train("Super cheap octocats for sale at GitHub.", True)
    d.train("Hi John, could you please come to my office by 3pm? Ding", False)

    m1 = "Cheap shoes for sale at DSW shoe store!"
    print(d.score(m1))

    m2 = "Hi mark could you please send me a copy of your machine learning homework? thanks"
    print(d.score(m2))
