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
import sys

from pyramid import httpexceptions
from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.path import DottedNameResolver
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import AppendSlashNotFoundViewFactory

from baka._compat import text_type
from .config import config_yaml, trafaret_yaml
from .log import log, logging_format
from .resources import METHODS, ViewDecorator, default_options_view, unsupported_method_view, _BakaExtensions
from .routes import add_simple_route
from .settings import SettingError


class Baka(object):

    __trafaret = trafaret_yaml

    def __init__(self, package, session_key=None,
                 authn_policy=None, authz_policy=None,
                 config_schema=False, **settings):
        """initial config for singleton baka framework

        :param import_name: the name of the application package
        :param settings: *optional dict settings for pyramid configuration
        """
        self.package = package
        self.config_schema = config_schema

        session_factory = UnencryptedCookieSessionFactoryConfig(session_key)
        settings.update({
            'session_factory': session_factory,
            'authentication_policy': authn_policy,
            'authorization_policy': authz_policy
        })
        self.config = self.configure(settings)
        self.config.begin()
        self.config.add_view(AppendSlashNotFoundViewFactory(), context=NotFound)
        self.config.add_directive('add_ext', self.add_ext_config)
        self.config.include(__name__)
        self.config.commit()
        self.registry = _BakaExtensions

        # Only set up a default log handler if the
        # end-user application didn't set anything up.
        if not (logging.root.handlers and log.level == logging.NOTSET and settings.get('LOGGING')):
            formatter = logging.Formatter(logging_format)
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.setLevel(logging.INFO)

        log.info('Baka Framework')

    def __call__(self, env, response):
        """Shortcut for :attr:`wsgi_app`."""
        return self.wsgi_app(env, response)

    def include(self, callable):
        self.config.include(callable)

    def exc_handler(self, exc, request):
        return request.get_response(exc)

    def include_schema(cls, config):
        cls.__trafaret = cls.__trafaret.merge(config)

    include_schema = classmethod(include_schema)

    @property
    def name(self):
        """The name of the application.  This is usually the import name
        with the difference that it's guessed from the run file if the
        import name is main.  This name is used as a display name when
        Baka needs the name of the application.  It can be set and overridden
        to change the value.
        """

        module = sys.modules[self.package]
        f = getattr(module, '__file__', '')
        if f in ['__init__.py', '__init__$py']:
            # Module is a package
            return module
        # Go up one level to get package
        package_name = module.__name__.rsplit('.', 1)[0]
        return sys.modules[package_name]

    def add_ext_config(self, config, name, directive):
        """ This does the same thing as :meth:`add_ext` but using for pyramid configuration
        :param config: the config from pyramid configuration object
        :param name: the name of directive
        :param directive: the callback function directive
        """
        self.add_ext(name, directive)

    def add_ext(self, name, directive):
        """ Registry of baka directive
        :param name: the name of directive
        :param directive: the callback function directive
        """
        if name in vars(self).keys():
            raise AttributeError(name)

        c = DottedNameResolver().maybe_resolve(directive)
        setattr(self, name, c)

    def configure(self, settings):
        """ This initial settings of pyramid Configurator
        :param settings: :dict settings of Configurator
        :return: pyramid.config.Configurator
        """
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

        # set from config file
        if self.config_schema:
            settings.update(
                config_yaml(self.package, _yaml=self.__trafaret))

        return Configurator(settings=settings)

    def resource(self, path, **kwargs):
        def decorator(wrapped):
            route_name = kwargs.pop("route_name", None)
            route_name = route_name or wrapped.__name__
            route_name = kwargs.pop("name", route_name)
            wrapped.route_name = route_name

            for method in METHODS:
                setattr(wrapped, method,
                        type('ViewDecorator%s' % method,
                             (ViewDecorator, object),
                             {'request_method': method,
                              'state': wrapped,
                              'kwargs': kwargs,
                              'config': self.config
                              }))

            # def callback(scanner, name, cls):
            self.config.add_route(route_name, path, factory=wrapped)
            self.config.add_view(default_options_view, route_name=route_name,
                                 request_method='OPTIONS', permission=NO_PERMISSION_REQUIRED)
            self.config.add_view(unsupported_method_view, route_name=route_name, renderer='json')

            # info = venusian.attach(wrapped, callback, 'pyramid', depth=depth)
            return wrapped

        return decorator

    def route(self, path, **kwargs):
        """A decorator that is used to register a view function for a
        given URL rule.  This does the same thing as :meth:`add_simple_route`
        but is intended for decorator usage::

            @app.route('/', renderer='todo:templates/index.html')
            def index(req):
                return {'baka', 'Hello World'}

            @app.route('/', renderer='json')
            def index(req):
                return {'baka', 'Hello World'}

            @app.route('/')
            def index(req):
                return {'baka', 'Hello World'}

        ```pyramid.view.view_config```
        A function, class or method :term:`decorator` which allows a
        developer to create view registrations nearer to a :term:`view
        callable` definition than use :term:`imperative
        configuration` to do the same.

        :param rule: the URL rule as string
        :param renderer: (default: json) the format templates for render in response view
        :param kwargs: supports the following keyword arguments:
                        ``context``, ``exception``, ``permission``, ``name``,
                        ``request_type``, ``route_name``, ``request_method``, ``request_param``,
                        ``containment``, ``xhr``, ``accept``, ``header``, ``path_info``,
                        ``custom_predicates``, ``decorator``, ``mapper``, ``http_cache``,
                        ``require_csrf``, ``match_param``, ``check_csrf``, ``physical_path``, and
                        ``view_options``.
        """
        kwargs['path'] = path

        def decorator(wrapped):
            """Attach the decorator with Venusian"""

            log.debug(kwargs.get('request_method', 'GET'))
            log.debug(kwargs.get('route_name', 'route_name'))

            # Default to not appending slash
            if not "append_slash" in kwargs:
                append_slash = False

            add_simple_route(self.config, wrapped, **kwargs)

            return wrapped

        return decorator

    def run(self, host=None, port=None, **options):
        """ application runner server for development stage. not for production.

        :param host: url host application server
        :param port: number of port
        :param options: dict options for werkzeug wsgi server
        """
        self.config.end()
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
        """ wsgi application instance
        :param env: environ wsgi
        :param response: response wsgi
        :return: wsgi middleware
        """
        self.config.end()
        app = self.config.make_wsgi_app()
        return app(env, response)

    def redirect(self, url):
        raise httpexceptions.HTTPFound(location=url)

    def listen(self, event_type=None):
        def decorator(func):
            self.config.add_subscriber(func, event_type)

        return decorator

    def notify(self, event):
        self.config.registry.notify(event)

    def exception_handler(self, **settings):
        def decorator(wrapped):
            settings['renderer'] = settings.get('renderer', 'json')
            settings['permission'] = settings.get('permission,', NO_PERMISSION_REQUIRED)

            target = DottedNameResolver().maybe_resolve(wrapped)

            def err_func(context, request):
                if not isinstance(context, Exception):
                    context = request.exception or context
                request.response.status = '509 {}'.format(text_type(context))
                # request.response.status_code = 500
                return target(context, request)

            self.config.add_view(err_func, context=Exception, **settings)

            return wrapped

        return decorator


    def error_handler(self, code, **settings):
        def decorator(wrapped):
            settings['renderer'] = settings.get('renderer', 'json')
            settings['permission'] = settings.get('permission,', NO_PERMISSION_REQUIRED)

            target = DottedNameResolver().maybe_resolve(wrapped)
            def err_func(context, request):
                if not isinstance(context, Exception):
                    context = request.exception or context
                request.response.status = context.status
                request.response.status_code = code
                return target(context, request)

            exc = type(httpexceptions.exception_response(code))
            log.info(exc)
            if exc is not None:
                view = err_func
                if exc is NotFound:
                    view = AppendSlashNotFoundViewFactory(err_func)
            else:
                exc = Exception

            self.config.add_view(view, context=exc, **settings)

            return wrapped

        return decorator


def includeme(config):
    config.include('.renderers')
    config.include('.routes')
