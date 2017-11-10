#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/textsum-textrank/word2vec/scripts/4.1.wikidata.replacer.py
# Author: Hai Liang Wang
# Date: 2017-11-04:09:59:45
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-04:09:59:45"


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

def replace_wikidata(f_input, f_output):
    with open(f_input, "r") as fin:
        if os.path.exists(f_output): os.remove(f_output)
        for x in fin.readlines():
            content = x.strip()
            content = data_processor.filter_full_to_half(content)
            content = data_processor.filter_date(content)
            content = data_processor.filter_number(content)
            content = data_processor.filter_url(content)
            content = data_processor.filter_name(content.split())
            content = data_processor.solo_tnumber_utterance(content) 
            # print("join_none_chinese_utterance ", " ".join(content))
            content = data_processor.join_none_chinese_utterance(content)
            # print("content ", content)
            try:
                if len(content) > 10:
                    data_processor.append_line_to_file( " ".join(content) + "\n", f_output)
            except Exception:
                pass            
# run testcase: python /Users/hain/ai/textsum-textrank/word2vec/scripts/4.1.wikidata.replacer.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_replace_wikidata(self):
        print("test replace_wikidata")
        f_from = os.path.join(curdir, os.path.pardir, os.path.pardir, "tmp", "zhwiki-latest-pages-articles.1020.seg")
        f_to = os.path.join(curdir, os.path.pardir, os.path.pardir, "tmp", "zhwiki-latest-pages-articles.1020.rep")
        replace_wikidata(f_from, f_to)


def test():
    unittest.main()

if __name__ == '__main__':
    test()
