# -*- coding: utf-8 -*-
"""
    
    ~~~~~~~~~
    
    :author: nanang.jobs@gmail.com
    :copyright: (c) 2017 by Nanang Suryadi.
    :license: BSD, see LICENSE for more details.
    
    response.py
"""
import time


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = timestamp()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print('elapsed time: %f ms' % self.msecs)


def timestamp():
    return int(time.time())


class JSONAPIResponse(Timer):
    """
        200 OK - Success
        400 Bad Request - The request was invalid.
        401 Not Authorized - Authentication credentials were missing or invalid.
        403 Forbidden - The request was understood, but it has been refused for some reason.
        404 Not Found - The requested URI does not exist.
        500 Internal Server Error - Some unexpected error has occurred.
        503 Service Unavailable - The API is currently not online
    """
    OK = (200, "OK")
    BAD_REQUEST = (400, "BAD REQUEST")
    NOT_AUTHORIZED = (401, "NOT AUTHORIZED")
    FORBIDDEN = (403, "FORBIDDEN")
    NOT_FOUND = (404, "NOT FOUND")
    INTERNAL_SERVER_ERROR = (500, "INTERNAL SERVER ERROR")
    SERVICE_UNAVAILABLE = (503, "SERVICE UNAVAILABLE")

    def __init__(self, response=None):
        self.Resp = response
        super(JSONAPIResponse, self).__init__()

    def to_json(self, confirm, **kwargs):
        code = kwargs.pop("code", JSONAPIResponse.OK[0])
        self.Resp.status_code = code
        self.__dict__ = {
            'code': code,
            'response': {
                'description': kwargs.pop('status', JSONAPIResponse.OK[1]),
                'elapsetime': float(format(self.msecs, '.4f')),
                'unix_timestamp': timestamp(),
                'confirm': confirm,
                'lang': 'id',
                'currency': 'IDR'
            }
        }
        self.__dict__.update(kwargs)
        return self.__dict__
