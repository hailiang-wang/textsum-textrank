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
sys.path.append(os.path.join(curdir, os.path.pardir))

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

def _levenshtein_distance(sentence1, sentence2):
    '''
    Return the Levenshtein distance between two strings.
    Based on:
        http://rosettacode.org/wiki/Levenshtein_distance#Python
    '''
    first = sentence1.split()
    second = sentence2.split()
    if len(first) > len(second):
        first, second = second, first
    distances = range(len(first) + 1)
    for index2, char2 in enumerate(second):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(first):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1],
                                             distances[index1 + 1],
                                             new_distances[-1])))
        distances = new_distances
    levenshtein = distances[-1]
    return 2 ** (-1 * levenshtein)

def _similarity_distance(s1, s2):
    '''
    compute similarity with distance measurement
    '''
    a = _sim_molecule(_get_wv(s1))
    b = _sim_molecule(_get_wv(s2))
    # https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.norm.html
    g = 1 / (np.linalg.norm(a - b) + 1)
    u = _levenshtein_distance(s1, s2)
    # print("_levenshtein_distance:", u)
    # print("word2vec:", g)
    r = g * 5 + u
    r = min(r , 1.0)

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


import unittest

# run testcase: python /Users/hain/ai/textsum-textrank/src/common/bm25test.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sim_sens(self):
        print("test_sim_sens")
        sen1 = ["计算出每篇文章的关键词", "计算出每篇文章的关键词" ,"每篇文章的关键词", "当然你会好奇这里的TF是什么"]
        sen2 = ["计算出每篇文章的关键词", "计算出每篇关键词" ,"计算出每篇文章", "IDF是什么"]
        for (x,y) in zip(sen1, sen2):
            print("相似度：%f, %s v.s. %s" % (compare(x, y), x, y))
            print("*"*20 + "\n")
def test():
    unittest.main()

if __name__ == '__main__':
    test()