# -*- coding: utf-8 -*-
"""
    baka.app
    ~~~~~~~~~
    This module implements the central WSGI application object.

    :copyright: (c) 2016 by Nanang Suryadi.
    :license: BSD, see LICENSE for more details.
"""
import logging
import logging.config
import os

from pyramid.config import Configurator
from pyramid.interfaces import IViewMapperFactory
from pyramid.path import DottedNameResolver
from .settings import SettingError
from .log import log, logging_format
import venusian
from zope.interface import Interface, Attribute, implementer


class Baka(object):
    def __init__(self, pathname, **settings):
        self.path = pathname
        self.config = self.configure(settings)
        self.config.add_directive('add_ext', self.add_ext_config)
        self.config.include(__name__)
        self.registry = _BakaExtensions

        # Only set up a default log handler if the
        # end-user application didn't set anything up.
        if not (logging.root.handlers and log.level == logging.NOTSET and settings.get('LOGGING')):
            formatter = logging.Formatter(logging_format)
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.setLevel(logging.INFO)

    def __getattr__(self, name):
        # allow directive extension names to work
        directives = getattr(self.registry, '_directives', {})
        c = directives.get(name)
        if c is None:
            raise AttributeError(name)

        # Create a bound method (works on both Py2 and Py3)
        # http://stackoverflow.com/a/1015405/209039
        m = c.__get__(self, self.__class__)
        return m

    def add_ext_config(self, config, name, directive):
        self.add_ext(name, directive)

    def add_ext(self, name, directive):
        c = DottedNameResolver().maybe_resolve(directive)
        if not hasattr(self.registry, '_directives'):
            self.registry._directives = {}
        self.registry._directives[name] = c

    def configure(self, settings):
        if settings.get('environ') is None:
            environ = os.environ
        if settings is None:
            settings = {}

        if settings.get('env') is not None:
            for s in settings.get('env'):
                try:
                    result = s(environ)
                except SettingError as e:
                    log.warn(e)

                if result is not None:
                    settings.update(result)

        if 'secret_key' not in settings:
            log.warn('No secret key provided: using transient key. Please '
                     'configure the secret_key setting or the SECRET_KEY '
                     'environment variable!')
            settings['secret_key'] = os.urandom(64)

        # Set up SQLAlchemy debug logging
        if 'debug_query' in settings:
            level = logging.INFO
            if settings['debug_query'] == 'trace':
                level = logging.DEBUG
            logging.getLogger('sqlalchemy.engine').setLevel(level)

        return Configurator(settings=settings)

    def route(self, path, **settings):
        settings['path'] = path

        def decorator(wrapped):
            """Attach the decorator with Venusian"""

            log.debug(settings.get('request_method', 'GET'))
            log.debug(settings.get('route_name', 'route_name'))

            def callback(scanner, _name, wrapped):
                """Register a view; called on config.scan"""
                config = scanner.config.with_package(info.module)

                # Default to not appending slash
                if not "append_slash" in settings:
                    append_slash = False

                # pylint: disable=W0142
                add_simple_route(config, wrapped, **settings)

            info = venusian.attach(wrapped, callback)

            if info.scope == 'class':  # pylint:disable=E1101
                # if the decorator was attached to a method in a class, or
                # otherwise executed at class scope, we need to set an
                # 'attr' into the settings if one isn't already in there
                if settings.get('attr') is None:
                    settings['attr'] = wrapped.__name__

            return wrapped

        return decorator

    def scan(self, _path=None):
        self.config.scan(_path or self.path)

    def run(self, host=None, port=None, **options):
        settings = self.config.get_settings()
        _host = '127.0.0.1'
        _port = 5000

        host = host or _host
        port = int(port or _port)
        options.setdefault('use_reloader', settings.get('debug_all'))
        options.setdefault('use_debugger', settings.get('debug_all'))

        from werkzeug.serving import run_simple
        run_simple(host, port, self.config.make_wsgi_app(), **options)

    def wsgi_app(self, env, response):
        app = self.config.make_wsgi_app()
        return app(env, response)

    def __call__(self, env, response):
        """Shortcut for :attr:`wsgi_app`."""
        return self.wsgi_app(env, response)

    def cetak(self):
        log.info('cetak')


"""Adaption of tomb_routes.
    This code is adoption of tomb_routes https://github.com/TombProject/tomb_routes created by John Anderson.
"""


def add_simple_route(
        config, target,
        append_slash=False, **kwargs):
    """Configuration directive that can be used to register a simple route to
    a view.

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
