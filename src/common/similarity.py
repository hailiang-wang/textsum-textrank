#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=========================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
# Author: Hai Liang Wang
# Date: 2017-09-27
#
#=========================================================================

"""
Chinese Synonyms for Natural Language Processing and Understanding.
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__ = "Hu Ying Xi<>, Hai Liang Wang<hailiang.hl.wang@gmail.com>"
__date__ = "2017-09-27"


import os
import sys
import numpy as np
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(curdir, os.path.pardir, os.path.pardir))

PLT = 2

if sys.version_info[0] < 3:
    default_stdout = sys.stdout
    default_stderr = sys.stderr
    reload(sys)
    sys.stdout = default_stdout
    sys.stderr = default_stderr
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"
else:
    PLT = 3

import json
import gzip
import shutil
from common.word2vec import KeyedVectors
from common.utils import any2utf8
from common.utils import any2unicode
import jieba.posseg as _tokenizer
import jieba

'''
globals
'''
_vectors = None
_stopwords = set()

'''
similarity
'''

# stopwords
_fin_stopwords_path = os.path.join(curdir, os.path.pardir, "resources", 'similarity.stopwords.txt')
def _load_stopwords(file_path):
    '''
    load stop words
    '''
    global _stopwords
    words = open(file_path, 'r')
    stopwords = words.readlines()
    for w in stopwords:
        _stopwords.add(any2unicode(w).strip())

print(">> similarity: loading stopwords ...")
_load_stopwords(_fin_stopwords_path)

def _segment_words(sen):
    '''
    segment words with jieba
    '''
    words, tags = [], []
    m = _tokenizer.cut(sen, HMM=True)  # HMM更好的识别新词
    for x in m:
        words.append(x.word)
        tags.append(x.flag)
    return words, tags

# vectors
_f_model = os.path.join(curdir, os.path.pardir, "resources", 'similarity.vocab.vector')
def _load_w2v(model_file=_f_model, binary=True):
    '''
    load word2vec model
    '''
    if not os.path.exists(model_file):
        raise Exception("Model file %s does not exist" % model_file)
    return KeyedVectors.load_word2vec_format(
        model_file, binary=binary, unicode_errors='ignore')
print(">> similarity: loading vectors ...")
_vectors = _load_w2v(model_file=_f_model)

_sim_molecule = lambda x: np.sum(x, axis=0)  # 分子

def _get_wv(sentence):
    '''
    get word2vec data by sentence
    sentence is segmented string.
    '''
    global _vectors
    vectors = []
    for y in sentence.split():
        y_ = any2unicode(y).strip()
        if y_ not in _stopwords:
            try:
                vectors.append(_vectors.word_vec(y_))
            except KeyError as error:
                print("not exist in w2v model: %s" % y_)
                # c.append(np.zeros((100,), dtype=float))
    return vectors


def _unigram_overlap(sentence1, sentence2):
    '''
    compute unigram overlap
    '''
    x = set(sentence1.split())
    y = set(sentence2.split())

    intersection = x & y
    union = x | y

    return ((float)(len(intersection)) / (float)(len(union)))


def _similarity_distance(s1, s2):
    '''
    compute similarity with distance measurement
    '''
    a = _sim_molecule(_get_wv(s1))
    b = _sim_molecule(_get_wv(s2))
    # https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.norm.html
    g = 1 / (np.linalg.norm(a - b) + 1)
    u = _unigram_overlap(s1, s2)
    r = g * 1.4 + u * 0.2
    r = min((r * 10 + 0.1) , 1.0)

    return float("%.3f" % r)


def compare(s1, s2, seg=True):
    '''
    compare similarity
    s1 : sentence1
    s2 : sentence2
    seg : True : The original sentences need jieba.cut
          Flase : The original sentences have been cut.
    '''
    assert len(s1) > 0 and len(s2) > 0, "The length of s1 and s2 should > 0."
    if seg:
        s1 = ' '.join(jieba.cut(s1))
        s2 = ' '.join(jieba.cut(s2))
    return _similarity_distance(s1, s2)

def main():
    pass


if __name__ == '__main__':
    main()