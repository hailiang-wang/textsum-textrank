#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/textsum-textrank/scripts/evaluate.combine.py
# Author: Hai Liang Wang
# Date: 2017-11-10:17:00:47
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-10:17:00:47"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import unittest
import json

# run testcase: python /Users/hain/ai/textsum-textrank/scripts/evaluate.combine.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_combine_eval_results(self):
        print("test_combine_eval_results")
        pairseq_ = os.path.join(curdir, os.path.pardir, "tmp", "select_title_output_1.json")
        textrank_ = os.path.join(curdir, os.path.pardir, "tmp", "text_rank_evaluate.json")
        output_ = os.path.join(curdir, os.path.pardir, "tmp", "output.json")
        pairseq_json = dict()
        with open(pairseq_, "r") as fin:
            pairseq_json = json.loads(fin.read())
            print("pairseq_json: %s" % len(pairseq_json.keys()))
            # assert len(pairseq_json.keys()) > 0, "empty pairseq_result"

        textrank_json = {}
        with open(textrank_, "r") as fin:
            textrank_json = json.loads(fin.read())
            print("textrank_json: %s" % len(textrank_json))

        raw_data = dict()

        for (x,y) in enumerate(textrank_json):

            raw_data[y["uuid"]] = dict({
                                       "content": y["content"],
                                       "headline": y["headline"],

                                       })

            if not y["uuid"] in pairseq_json:

                pairseq_json[y["uuid"]] = [dict({
                             "feature_id": "textrank",
                             "rank": y["rank"],
                             "keywords": y["keywords"] if "keywords" in y else None
                             })]
            else:
                pairseq_json[y["uuid"]].append(dict({
                             "feature_id": "textrank",
                             "rank": y["rank"],
                             "keywords": y["keywords"] if "keywords" in y else None
                             }))

        if os.path.exists(output_): os.remove(output_)
        with open(output_, "w") as fout:
            fout.write(json.dumps(dict({
                                       "docs": raw_data,
                                       "textsum": pairseq_json
                                       }), ensure_ascii=False))

def test():
    unittest.main()

if __name__ == '__main__':
    test()
