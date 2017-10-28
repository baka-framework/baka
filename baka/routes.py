import os

from pyramid.httpexceptions import WSGIHTTPException
from pyramid.interfaces import IViewMapperFactory, IExceptionResponse
from pyramid.path import DottedNameResolver
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.settings import asbool

from .log import log


def add_simple_route(
        config, target,
        append_slash=False, **kwargs):
    """Configuration directive that can be used to register a simple route to
    a view. Connects a URL rule.  Works exactly like the :meth:`route`decorator

    Examples:

    with view callable::

        config.add_simple_route(
            '/path/to/view', view_callable,
            renderer='json'
        )

    with dotted path to view callable::

        config.add_simple_route(
            '/path/to/view', 'dotted.path.to.view_callable',
            renderer='json'
        )
    """

    target = DottedNameResolver().maybe_resolve(target)
    mapper = config.get_routes_mapper()

    log.debug(kwargs.get('request_method', 'GET'))
    log.debug(kwargs.get('route_name', 'route_name'))
    # TODO: modified untuk case url sama beda method request
    kwargs['request_method'] = kwargs.get('request_method', 'GET')
    kwargs['renderer'] = kwargs.get('renderer', 'json')  # default render json format

    # route_method = kwargs.get("request_method", 'GET')
    # route_method = '__'.join([target.__name__, route_method])
    add_route = True

    route_name = kwargs.pop("route_name", None)
    route_name = route_name or target.__name__
    route_name = kwargs.pop("name", route_name)
    # route_name_count = 0

    # Arguments passed to route
    route_kwargs = {}

    if 'accept' in kwargs:
        val = kwargs.pop('accept')
        route_kwargs['accept'] = val

    # For Resource Context Factory
    if 'factory' in kwargs:
        val = kwargs.pop('factory')
        route_kwargs['factory'] = val

    # Make it possible to custom_predicates = in the simple_route
    custom_predicates = kwargs.pop('custom_predicates', None)
    if custom_predicates:
        route_kwargs["custom_predicates"] = custom_predicates

    if 'attr' in kwargs:
        route_name += '.' + kwargs['attr']
    path = kwargs.pop('path', None)
    for _route in mapper.get_routes():
        if path == _route.pattern:
            route_name = _route.name
            # log.debug(':='.join(['mapper route', str(add_route)]))
            # no need add route
            add_route = False
            break

    # routes = {route.name: route for route in mapper.get_routes()}
    # orig_route_name = route_name

    # while route_name in routes:
    #     route_name = '%s_%s' % (orig_route_name, route_name_count)
    #     route_name_count += 1

    current_pregen = kwargs.pop('pregenerator', None)

    def pregen(request, elements, kwargs):
        if 'optional_slash' not in kwargs:
            kwargs['optional_slash'] = ''

        if current_pregen is not None:
            return current_pregen(request, elements, kwargs)
        else:
            return elements, kwargs

    orig_route_prefix = config.route_prefix
    # We are nested with a route_prefix but are trying to
    # register a default route, so clear the route prefix
    # and register the route there.
    if (path == '/' or path == '') and config.route_prefix:
        path = config.route_prefix
        config.route_prefix = ''
    if add_route:
        if append_slash:
            path += '{optional_slash:/?}'
            config.add_route(
                route_name, path, pregenerator=pregen,
                **route_kwargs
            )
        else:
            config.add_route(
                route_name, path, pregenerator=current_pregen,
                **route_kwargs
            )

    kwargs['route_name'] = route_name

    if 'mapper' not in kwargs:
        mapper = config.registry.queryUtility(IViewMapperFactory)
        kwargs['mapper'] = mapper

    config.add_view(target, **kwargs)
    config.commit()
    config.route_prefix = orig_route_prefix


def includeme(config):
    config.add_directive('add_simple_route', add_simple_route)
    settings = config.registry.settings
    settings['baka.debug'] = \
        settings.get('debug_all') or \
        settings.get('pyramid.debug_all') or \
        asbool(os.environ.get('PYRAMID_DEBUG_ALL')) or \
        asbool(os.environ.get('BAKA_DEBUG'))
    if not settings['baka.debug']:
        config.add_view('baka.error.generic',
                        context=Exception, renderer='json',
                        permission=NO_PERMISSION_REQUIRED)
    config.add_view('baka.error.http_error', context=IExceptionResponse, renderer='json')
    config.add_view('baka.error.http_error', context=WSGIHTTPException, renderer='json')
    config.add_notfound_view('baka.error.notfound', renderer='json')
    config.add_forbidden_view('baka.error.forbidden', renderer='json')
