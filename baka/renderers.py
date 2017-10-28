import enum
import json
from datetime import datetime, date
from decimal import Decimal

import bson
from bson.objectid import ObjectId

from .response import JSONAPIResponse


class EnumInt(object):
    def __init__(self, value, values):
        self.value = value
        self._values = values

    @property
    def title(self):
        return self.value if self.value is None else self._values[self.value][1]

    @property
    def key(self):
        return self.value is not None and self._values[self.value][0]

    def __eq__(self, other):
        values = list(map(lambda x: x[0], self._values))
        return (other in values) and self.value == values.index(other)

    def __str__(self):
        return self.value if self.value is None else u"%s, %s" % (
            self.value, self._values[self.value][1]
        )

    def __repr__(self):
        return u"EnumInt(%s)" % self

    def serialize(self):
        return {'key': self.key, 'value': self.value, 'title': self.title}


def json_dumps(o):
    return json.dumps(o, cls=JSONEncoder)


def json_loads(s):
    return json.loads(s, parse_float=Decimal)


def bson_dumps(o):
    return bson.dumps(o)


def bson_loads(s):
    return bson.loads(s)


class Factory(object):

    #XXX Permit to extend formats?

    formatters = {
        'application/json': json_dumps,
        'application/bson': bson_dumps,
    }

    def __init__(self, info):
        """ Constructor: info will be an oect having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """
        self.info = info

    def __call__(self, value, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode oect).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        # (e.g. view, context, and request). """
        request = system['request']
        with JSONAPIResponse(request.response) as resp:
            _in = u'Failed'
            code, status = JSONAPIResponse.OK
            settings = self.info.settings

            format = request.accept.best_match([
                'application/json',
                'application/bson',
            ])
            request.response.content_type = format
            if settings.get('baka')['meta']:
                meta = {'meta': settings['baka'].get('meta', {})}
        value = resp.to_json(
            _in, code=code,
            status=status, message=value, **meta)

        return self.formatters[format](value)


class JSONEncoder(json.JSONEncoder):
    """Custom encoder that supports extra types.

    Supported types: date, datetime, Decimal, bson.objectid.ObjectId.
    """

    def default(self, o):
        # for Enum Type
        if isinstance(o, enum.Enum):
            return o.value

        # for Enum Select Integer
        if isinstance(o, EnumInt):
            return o.key

        if isinstance(o, (datetime, date)):
            return o.isoformat()

        if isinstance(o, Decimal):
            return _number_str(o)

        if isinstance(o, ObjectId):
            return str(o)

        return super(JSONEncoder, self).default(o)


class _number_str(float):
    # kludge to have decimals correctly output as JSON numbers;
    # converting them to strings would cause extra quotes

    def __init__(self, o):
        self.o = o

    def __repr__(self):
        return str(self.o)


def includeme(config):
    config.add_renderer('restful', Factory)
