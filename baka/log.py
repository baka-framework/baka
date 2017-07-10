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
