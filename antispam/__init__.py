#!/usr/bin/env python
# Copyright (c) 2015 Peixuan Ding
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import print_function

import re
import os
import sys
try:
    import cPickle as pickle
except:
    import pickle
from functools import reduce

__version__ = "0.0.10"


class Model(object):
    """Save & Load the model in/from the file system using Python's pickle
    module.
    """
    DEFAULT_DATA_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "model.dat")

    def __init__(self, file_path=None, create_new=False):
        """Constructs a Model object by the indicated ``file_path``, if the
        file does not exist, create a new file and contruct a empty model.

        :param file_path: (optional) Path for the model file indicated, if
            path is not indicated, use the built-in model file provided by
            the author, which is located in the ``antispam`` package folder.

        :param create_new: (option) Boolean. If ``True``, create an empty
            model. ``file_path`` will be used when saving the model. If there
            is an existing model file on the path, the existing model file
            will be overwritten.
        """
        self.file_path = file_path if file_path else self.DEFAULT_DATA_PATH
        self.create_new = create_new
        if self.create_new:
            self.spam_count_total = 0
            self.ham_count_total = 0
            self.token_table = {}
        else:
            self.spam_count_total, self.ham_count_total, self.token_table = self.load(file_path)

    def load(self, file_path=None):
        """Load the serialized file from the specified file_path, and return
        ``spam_count_total``, ``ham_count_total`` and ``token_table``.

        :param file_path: (optional) Path for the model file. If the path does
            not exist, create a new one.
        """
        file_path = file_path if file_path else self.DEFAULT_DATA_PATH
        if not os.path.exists(file_path):
            with open(file_path, 'a'):
                os.utime(file_path, None)
        with open(file_path, 'rb') as f:
            try:
                return pickle.load(f)
            except:
                return (0, 0, {})

    def save(self):
        """Serialize the model using Python's pickle module, and save the
        serialized modle as a file which is indicated by ``self.file_path``."""
        with open(self.file_path, 'wb') as f:
            pickle.dump(
                (self.spam_count_total, self.ham_count_total,
                 self.token_table), f, -1)


class Detector(object):
    """A baysian spam filter

    :param path: (optional) Path for the model file, will be passes to
        ``Model`` and construct a ``Model`` object based on ``path``.
    """
    TOKENS_RE = re.compile(r"\$?\d*(?:[.,]\d+)+|\w+-\w+|\w+", re.U)
    INIT_RATING = 0.4

    def __init__(self, path=None, create_new=False):
        self.model = Model(path, create_new)

    def _get_word_list(self, msg):
        """Return a list of strings which contains only alphabetic letters,
        and keep only the words with a length greater than 2.
        """
        return filter(lambda s: len(s) > 2,
                      self.TOKENS_RE.findall(msg.lower()))

    def save(self):
        """Save ``self.model`` based on ``self.model.file_path``.
        """
        self.model.save()

    def train(self, msg, is_spam):
        """Train the model.

        :param msg: Message in string format.
        :param is_spam: Boolean. If True, train the message as a spam, if
            False, train the message as a ham.
        """
        token_table = self.model.token_table
        if is_spam:
            self.model.spam_count_total += 1
        else:
            self.model.ham_count_total += 1

        for word in self._get_word_list(msg.lower()):
            if word in token_table:
                token = token_table[word]
                if is_spam:
                    token[1] += 1
                else:
                    token[0] += 1
            else:
                token_table[word] = [0, 1] if is_spam else [1, 0]

    def score(self, msg):
        """Calculate and return the spam score of a msg. The higher the score,
        the stronger the liklihood that the msg is a spam is.

        :param msg: Message in string format.
        """
        token_table = self.model.token_table
        hashes = self._get_word_list(msg.lower())
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
                    rating = self.INIT_RATING
            else:
                rating = self.INIT_RATING
            ratings.append(rating)

        if (len(ratings) > 20):
            ratings.sort()
            ratings = ratings[:10] + ratings[-10:]

        product = reduce(lambda x, y: x * y, ratings)
        alt_product = reduce(lambda x, y: x * y, map(lambda r: 1.0 - r,
                                                     ratings))
        return product / (product + alt_product)

    def is_spam(self, msg):
        """Decide whether the message is a spam or not.
        """
        return self.score(msg) > 0.9


module = sys.modules[__name__]


def score(msg):
    """Score the message based on the built-in model.

    :param msg: Message to be scored in string format.
    """
    if hasattr(module, 'obj'):
        detector = getattr(module, 'obj')
        return detector.score(msg)
    else:
        detector = Detector()
        setattr(module, 'obj', detector)
        return detector.score(msg)


def is_spam(msg):
    """Decide whether the message is a spam or not based on the built-in model.

    :param msg: Message to be classified in string format.
    """
    return score(msg) > 0.9


if __name__ == "__main__":
    d = Detector(create_new=True)

    d.train("Super cheap octocats for sale at GitHub.", True)
    d.train("Hi John, could you please come to my office by 3pm? Ding", False)

    m1 = "Cheap shoes for sale at DSW shoe store!"
    print(d.score(m1))

    m2 = "Hi mark could you please send me a copy of your machine learning homework? thanks"
    print(d.score(m2))
