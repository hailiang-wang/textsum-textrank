#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/tmp/clean-vocab.py
# Author: Hai Liang Wang
# Date: 2017-11-05:12:50:09
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-11-05:12:50:09"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import unittest

# run testcase: python /Users/hain/tmp/clean-vocab.py Test.testExample
class Test(unittest.TestCase):
    '''
    
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_clean_digit(self):
        f_from = os.path.join(curdir, "news.vocab")
        f_to = os.path.join(curdir, "news.text.vocab")
        f_to_digit = os.path.join(curdir, "news.digit.vocab")
        if os.path.exists(f_to): os.remove(f_to)
        if os.path.exists(f_to_digit): os.remove(f_to_digit)
        with open(f_from, "r") as fin, open(f_to, "w") as fout, open(f_to_digit, "w") as fout_d:
            for x in fin.readlines():
                o = x.split()
                assert len(o) == 2, "not two member"
                w = o[0]
                f = o[1]
                # todo check w if digit
                try:
                    float(w)
                    fout_d.write("%s %s\n" % (w, f))
                except:
                    print("%s not a number" % w)
                    fout.write("%s %s\n" % (w, f))
                    continue
                print("%s is a number" % w)

def test():
    unittest.main()

if __name__ == '__main__':
    test()
