#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/trio/chat-log-burnish/purelog/common/log.py
# Author: Hai Liang Wang
# Date: 2017-10-25:16:58:57
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-10-25:16:58:57"


import os
import sys
import logging
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = os.path.join(curdir, os.path.pardir, os.path.pardir, 'logs', 'root.log')
print('Saving logs into', log_file)

LOG_LVL= "INFO" if not "TXT_CLS_LOG_LVL" in os.environ else os.environ["TXT_CLS_LOG_LVL"]

fh = logging.FileHandler(log_file)
fh.setFormatter(formatter)
fh.setLevel(LOG_LVL)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(LOG_LVL)

def set_log_level(level = "DEBUG"):
    fh.setLevel(level)
    ch.setLevel(level)

def getLogger(logger_name, level = "DEBUG"):
    logger = logging.getLogger(logger_name)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.setLevel(level) # logging.DEBUG
    return logger

if __name__ == "__main__":
    logger = getLogger('foo')
    logger.info('bar')