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

import venusian
from pyramid.config import Configurator, ConfigurationError
from pyramid.path import DottedNameResolver
from pyramid.security import NO_PERMISSION_REQUIRED

from .config import config_yaml, merge_yaml, trafaret_yaml
from .log import log, logging_format
from .resources import METHODS, ViewDecorator, default_options_view, unsupported_method_view, _BakaExtensions
from .routes import add_simple_route
from .settings import SettingError


class Baka(object):
    def __init__(self, pathname, **settings):
        """initial config for singleton baka framework

        :param import_name: the name of the application package
        :param settings: *optional dict settings for pyramid configuration
        """
        self.import_name = pathname
        self.settings = settings
        self.__include = {}
        self.__trafaret = trafaret_yaml

        # Only set up a default log handler if the
        # end-user application didn't set anything up.
        if not (logging.root.handlers and log.level == logging.NOTSET and settings.get('LOGGING')):
            formatter = logging.Formatter(logging_format)
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.setLevel(logging.INFO)

    def config_schema(self, config):
        self.__trafaret = self.__trafaret.merge(config)

    @property
    def name(self):
        """The name of the application.  This is usually the import name
        with the difference that it's guessed from the run file if the
        import name is main.  This name is used as a display name when
        Baka needs the name of the application.  It can be set and overridden
        to change the value.
        """

        module = sys.modules[self.import_name]
        f = getattr(module, '__file__', '')
        if f in ['__init__.py', '__init__$py']:
            # Module is a package
            return module
        # Go up one level to get package
        package_name = module.__name__.rsplit('.', 1)[0]
        return sys.modules[package_name]

    # recurssion error for getting attribute name
    # def __getattr__(self, name):
    #     """ built-in method for get attribute baka object
    #     :param name: selector
    #     :return:
    #     """
    #     # allow directive extension names to work
    #     directives = getattr(self.registry, '_directives', {})
    #     c = directives.get(name)
    #     if c is None:
    #         raise AttributeError(name)
    #
    #     # Create a bound method (works on both Py2 and Py3)
    #     # http://stackoverflow.com/a/1015405/209039
    #     m = c.__get__(self, self.__class__)
    #     return m

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
        if name in vars(name).keys():
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
        settings.update(
            config_yaml(self.import_name, _yaml=self.__trafaret))
        return Configurator(settings=settings)

    def resource(self, path, **kwargs):
        def decorator(wrapped, depth=1):
            route_name = kwargs.pop("route_name", None)
            route_name = route_name or wrapped.__name__
            route_name = kwargs.pop("name", route_name)
            wrapped.route_name = route_name

            def callback(scanner, name, cls):
                config = scanner.config.with_package(info.module)
                config.add_route(route_name, path, factory=cls)
                config.add_view(default_options_view, route_name=route_name,
                                request_method='OPTIONS', permission=NO_PERMISSION_REQUIRED)
                config.add_view(unsupported_method_view, route_name=route_name, renderer='json')

            for method in METHODS:
                setattr(wrapped, method, type('ViewDecorator%s' % method,
                                              (ViewDecorator, object),
                                              {'request_method': method,
                                               'state': wrapped,
                                               'kwargs': kwargs}))
            info = venusian.attach(wrapped, callback, 'pyramid', depth=depth)
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

            def callback(scanner, _name, wrapped):
                """Register a view; called on config.scan"""
                config = scanner.config.with_package(info.module)

                # Default to not appending slash
                if not "append_slash" in kwargs:
                    append_slash = False

                # pylint: disable=W0142
                add_simple_route(config, wrapped, **kwargs)

            info = venusian.attach(wrapped, callback)

            if info.scope == 'class':  # pylint:disable=E1101
                # if the decorator was attached to a method in a class, or
                # otherwise executed at class scope, we need to set an
                # 'attr' into the settings if one isn't already in there
                if kwargs.get('attr') is None:
                    kwargs['attr'] = wrapped.__name__

            return wrapped

        return decorator

    def _get_package(self, dotted):
        """ get baka application package
        :param dotted: path of package
        :return: package of baka application name
        """
        module = sys.modules[dotted]
        f = getattr(module, '__file__', '')
        if f in ['__init__.py', '__init__$py']:
            # Module is a package
            return module
        # Go up one level to get package
        package_name = module.__name__.rsplit('.', 1)[0]
        return sys.modules[package_name]

    def include(self, callable):
        """ Include a configuration callable, to support imperative
        application extensibility.

        .. warning:: In versions of :app:`Pyramid` prior to 1.2, this
            function accepted ``*callables``, but this has been changed
            to support only a single callable.

        A configuration callable should be a callable that accepts a single
        argument named ``config``, which will be an instance of a
        :term:`Configurator`.  However, be warned that it will not be the same
        configurator instance on which you call this method.  The
        code which runs as a result of calling the callable should invoke
        methods on the configurator passed to it which add configuration
        state.  The return value of a callable will be ignored.

        Values allowed to be presented via the ``callable`` argument to
        this method: any callable Python object or any :term:`dotted Python
        name` which resolves to a callable Python object.  It may also be a
        Python :term:`module`, in which case, the module will be searched for
        a callable named ``includeme``, which will be treated as the
        configuration callable.

        For example, if the ``includeme`` function below lives in a module
        named ``myapp.myconfig``:

        .. code-block:: python
           :linenos:

           # myapp.myconfig module

           def my_view(request):
               from pyramid.response import Response
               return Response('OK')

           def includeme(config):
               config.add_view(my_view)

        You might cause it to be included within your Baka application like
        so:

        .. code-block:: python
           :linenos:

           from pyramid.config import Configurator

           def main(global_config, **settings):
               config = Configurator()
               config.include('myapp.myconfig.includeme')

        :param path:
        """

        _resolver = DottedNameResolver(self.name)
        _callable = None
        try:
            modules = self._get_package(callable)
            _callable = _resolver.maybe_resolve(modules)
        except KeyError:
            _callable = _resolver.maybe_resolve(callable)
        finally:
            if _callable is None:
                raise ConfigurationError(
                    'No source file for module %r (.py file must exist, '
                    'refusing to use orphan .pyc or .pyo file).' % _callable)
            self.__include[_callable.__name__] = _callable

    def _configure(self):
        self.config = self.configure(self.settings)
        self.config.add_directive('add_ext', self.add_ext_config)
        self.config.include(__name__)
        self.registry = _BakaExtensions

        # pull list include modules
        for _callable in self.__include:
            self.config.include(_callable)

    def scan(self, path=None):
        self._configure()
        """ Venusian scanner config
        :param path:
        """
        path = self._get_package(path or self.import_name)
        _resolver = DottedNameResolver(self.name)
        path = _resolver.maybe_resolve(path)
        log.info(path)
        self.config.scan(path)

    def run(self, host=None, port=None, **options):
        """ application runner server for development stage. not for production.

        :param host: url host application server
        :param port: number of port
        :param options: dict options for werkzeug wsgi server
        """
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

        app = self.config.make_wsgi_app()
        return app(env, response)

    @classmethod
    def add_config(cls, cfg):
        cls.trafaret = merge_yaml(cls, cfg)

    def __call__(self, env, response):
        """Shortcut for :attr:`wsgi_app`."""
        return self.wsgi_app(env, response)


def includeme(config):
    config.include('.renderers')
    config.include('.routes')
