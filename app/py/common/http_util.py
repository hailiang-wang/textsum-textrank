#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# File: /Users/hain/trio/chat-log-burnish/purelog/common/http_util.py
# Author: Hai Liang Wang
# Date: 2017-10-25:16:56:13
#
#===============================================================================

"""
   
"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-10-25:16:56:13"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(curdir, os.path.pardir))

from common import log
import json
logger = log.getLogger("common:http")

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

def is_json_headers(headers):
    '''
    verify the headers for REST API
    '''
    if headers is None: return False
    rc = True
    if not "Content-Type" in headers:
        return False
    if not headers["Content-Type"].startswith(
            "application/json"):
        return False
    if not "Accept" in headers:
        return False
    if not headers["Accept"].startswith(
            "application/json"):
        return False
    return rc