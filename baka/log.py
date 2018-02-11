# -*- coding: utf-8 -*-
"""
    Log Module untuk handle pesan logging
    ~~~~~~~~~
    
    :copyright: (c) 2017 by Nanang Suryadi.
    :license: BSD, see LICENSE for more details.
    
    log.py
"""
import logging

logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():%(lineno)d: "
logging_format += "%(message)s"

log = logging.getLogger('Baka')


def _logging_format(settings):
    # Only set up a default log handler if the
    # end-user application didn't set anything up.
    if not (logging.root.handlers and log.level == logging.NOTSET and settings.get('LOGGING')):
        formatter = logging.Formatter(logging_format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(logging.INFO)
