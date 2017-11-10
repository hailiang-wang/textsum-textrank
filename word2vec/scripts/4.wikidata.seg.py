#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/textsum-textrank/word2vec/scripts/4.wikidata.seg.py
# Author: Hai Liang Wang
# Date: 2017-11-03:10:56:45
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-03:10:56:45"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
print("curdir:", os.path.join(curdir, os.path.pardir, os.path.pardir, "src"))
sys.path.append(os.path.join(curdir, os.path.pardir, os.path.pardir, "src"))

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import unittest
import data_processor  

def process_wikidata(f_input, f_output):
    if os.path.exists(f_output): os.remove(f_output)
    with open(f_input, "r") as fin:
        for x in fin.readlines():
            w, _ = data_processor.word_segment(x.strip())
            if len(w) > 5 and not "doc" in w:
                data_processor.append_line_to_file(" ".join(w) + "\n", f_output)
    print("done.")

# run testcase: python /Users/hain/ai/textsum-textrank/word2vec/scripts/4.wikidata.seg.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_process_wikidata(self):
        f_from = os.path.join(curdir, os.path.pardir, os.path.pardir, "tmp", "zhwiki-latest-pages-articles.1020.chs.normalized")
        f_to = os.path.join(curdir, os.path.pardir, os.path.pardir, "tmp", "zhwiki-latest-pages-articles.1020.seg")
        process_wikidata(f_from, f_to)

    def test_sen_seg(self):
        sen = "习近平向晋升上将军衔的张升民颁发命令状。"
        print("before seg:",sen)
        w, t = data_processor.word_segment(sen)
        result = ""
        for (x,y) in zip(w, t):
            result += "%s %s /"% (x, y)
        print("seg: %s" % result)


def test():
    unittest.main()

if __name__ == '__main__':
    test()
