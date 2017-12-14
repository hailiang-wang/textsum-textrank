#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=========================================================================
#
# Copyright (c) 2017 <> All Rights Reserved
#
#
# Author: Hai Liang Wang
# Date: 2017-10-25:14:49:34
#
#=========================================================================

"""

"""
from __future__ import print_function
from __future__ import division

__copyright__ = "Copyright (c) 2017 . All Rights Reserved"
__author__ = "Hai Liang Wang"
__date__ = "2017-10-25:14:49:34"


import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"

import json
from flask import Flask
from flask import request
from flask import redirect
from flask import jsonify
app = Flask(__name__)

from common import log
from common import http_util
logger = log.getLogger("text-classifier:server")

import summarizer

sz = summarizer.Summarizer()

@app.route('/api/summary', methods=["POST"])
def api_summary():
    '''
    generate summary
    '''
    logger.debug("api_summary")
    result = dict({
                  "rc": None
                  })
    try:
        if http_util.is_json_headers(request.headers):
            req = json.loads(request.get_data())
            if "content" in req:
                abstract = sz.extract(content = req["content"], rate = 140)
                result["rc"] = 1
                result["data"] = abstract
            else:
                result["rc"] = 0
                result["error"] = "Invalid body."
        else:
            # exception
            return json.dumps(dict({"rc": "0", "error": "bad headers or body, require Content-Type and Accept in headers."}))
    except Exception as e:
        result["rc"] = 0
        result["error"] = str(e)
    return json.dumps(result, ensure_ascii=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10030)
