# -*- coding: utf-8 -*-
"""

    ~~~~~~~~~

    :copyright: (c) 2017 by Nanang Suryadi.
    :license: BSD, see LICENSE for more details.

    wsgi.py
"""
from simpleapp.app import app

app.run(use_reloader=True)
