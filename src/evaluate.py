#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/ai/textsum-textrank/src/evaluate.py
# Author: Hai Liang Wang
# Date: 2017-11-06:16:24:43
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-06:16:24:43"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import unittest
import data_processor
import json
import summarizer

sumz = summarizer.Summarizer()


# run testcase: python /Users/hain/ai/textsum-textrank/src/evaluate.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_evaluate_gf_data(self):
        print("test_evaluate_gf_data")
        f_from = os.path.join(curdir, "resources", "info500.json")
        f_to = os.path.join(curdir, os.path.pardir, "tmp", "evaluate.json")
        f_trace = os.path.join(curdir, os.path.pardir, "tmp", "evaluate.trace")
        if os.path.exists(f_to): os.remove(f_to)
        if os.path.exists(f_trace): os.remove(f_trace)
        output = []
        trace = []
        trace.append("#top1s\ttop1\tcontent tokens\n")
        with open(f_from, "r") as fin:
            for x in fin.readlines():
                o = json.loads(x.strip())
                content = o["content"]
                title = o["title"]
                abstract, scores = sumz.extract(content)
                if len(scores) > 0:
                    output.append({
                                  "content": content,
                                  "headline": title,
                                  "predict": "%s %s" %(abstract[0] if len(abstract) > 0 else "",  abstract[1] if len(abstract) > 1 else ""),
                                  "_id": o["_id"],
                                  "uuid": o["uuid"],
                                  "rank": "<br><br>".join(["score: %s| %s" % (b ,a) for (a, b) in zip(abstract, scores)])
                                  })
                    tokens = sumz.tokenlize(content)
                    # print("scores[0]:", scores[0])
                    # print("abstract[0]:", abstract[0])
                    # print("tokens:", tokens)
                    trace.append("%f\t%s\t%s\n" %(scores[0], abstract[0], " ".join(tokens)))
            
        with open(f_trace, "w") as fout:
            fout.writelines(trace)

        with open(f_to, "w") as fout:
            fout.write(json.dumps(output, ensure_ascii=False))


def test():
    unittest.main()

if __name__ == '__main__':
    test()
