import venusian
from pyramid.httpexceptions import HTTPNoContent
from zope.interface import implementer, Interface, Attribute

METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

"""
    Adaption of Event Resources Routes.
    This code is adoption of 
    Event Resources from https://github.com/wichert/rest_toolkit
"""

class BaseDecorator(object):
    def __call__(self, wrapped, depth=1):
        info = venusian.attach(wrapped, self.callback, 'pyramid', depth=depth)
        self.module = info.module
        return wrapped


class ViewDecorator(BaseDecorator):
    """Base class for HTTP request method decorators for resources.

    This class should never be used directly. It is used internally to create
    the ``DELETE``, ``GET``, ``OPTIONS``, ``PATCH``, ``POST`` and ``PUT``
    decorators for resources classes when the :py:func:`resource` decorator is
    used.

    .. code-block:: python
       :linenos:

       @MyResource.GET()
       def get_view_for_my_resource(resource, request):
           '''Handle GET requests for MyResource.
           '''
    """
    default_arguments = {'renderer': 'json'}

    def __init__(self, **kw):
        self.view_arguments = self.default_arguments.copy()
        self.view_arguments.update(self.kwargs)
        self.view_arguments.update(kw)

    def callback(self, scanner, name, view):
        config = scanner.config.with_package(self.module)
        route_name = self.state.route_name
        # self.state.add_method(self.request_method, view)
        config.add_view(view,
                route_name=route_name,
                request_method=self.request_method,
                context=self.state,
                **self.view_arguments)


def unsupported_method_view(resource, request):
    request.response.status_int = 405
    return {'message': 'Unsupported HTTP method'}


def default_options_view(resource, request, methods=None):
    """Default OPTIONS view for resources."""
    response = HTTPNoContent()
    methods = {'OPTIONS'} if methods is None else methods
    response.headers['Access-Control-Allow-Methods'] = ', '.join(methods)
    return response


class IBakaExtensions(Interface):
    """ Marker interface for storing baka extensions (properties and
    methods) which will be added to the baka object."""
    descriptors = Attribute(
        """A list of descriptors that will be added to each baka singleton.""")
    methods = Attribute(
        """A list of methods to be added to baka singleton.""")


@implementer(IBakaExtensions)
class _BakaExtensions(object):
    def __init__(self):
        self.descriptors = {}
        self.methods = {}
