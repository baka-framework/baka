Baka Framework
==============

`Baka Framework <https://github.com/baka-framework/baka>`_. is Baka Framework is web application framework based on Pyramid.


Usage
-----

You can use these as base classes for declarative model definitions, e.g.

.. code:: python

    from baka import Baka
    from baka.log import log

    options = {
        'LOGGING': True,
        'secret_key': 'kuncirahasia'
    }
    app = Baka(__name__, **options)

    # route method
    @app.route('/')
    def index_page(req):
        log.info(req)
        return {'Baka': 'Hello World!'}


    @app.route('/home')
    def home_page(req):
        log.info(req)
        return {'Route': 'home'}


    # root resources routes
    class ResourcesPage(object):
        def __init__(self, request):
            self._name = 'Resource Page'
            log.info(request.params)


    # GET resource method
    @ResourcesPage.GET()
    def resources_page_get(root, request):
        return {
            'hello': 'Get Hello resources from Page root %s ' % page._name
        }

    app.scan()



Include Module
--------------

using baka include, you can mixing separate module in any different file and module package.

.. code:: python

    in other file: testbaka/view_user.py

    from .app import app


    @app.route('/users')
    def user(req):
        return {'users': 'all data'}

    def includeme(config):
        config.scan()

    file: testbaka/app.py

    from baka import Baka
    from baka.log import log


    app = Baka(__name__)
    # include from file view_user.py
    app.include('testbaka.view_user')

    @app.route('/')
    def index_page(req):
        log.info(req)
        return {'Baka': 'Hello World!'}


    @app.route('/home')
    def home_page(req):
        log.info(req)
        return {'Route': 'home'}

    app.scan()


App Folder
---------

For App Structure Folder

.. code:: html

    - root
        - package (AppBaka)
            - config
                - config.yaml # use for baka default configuration
            - __init__.py # the code goes in here
            - wsgi.py # for running in wsgi container e.g gunicorn
        - run.py # running development server


Default Configuration Baka from ``config.yaml``

.. code:: yaml

    package: AppBaka # mandatory for root package
    version: 0.1.0 # optional
    baka:
        debug_all: True # mandatory for debug environment
        meta:
            version: 0.1.0 # mandatory for json response version


WSGI Container Application Server ``wsgi.py``

.. code:: python

    # -*- coding: utf-8 -*-
    """
        WSGI Application Server
        ~~~~~~~~~

        :author: nanang.jobs@gmail.com
        :copyright: (c) 2017 by Nanang Suryadi.
        :license: BSD, see LICENSE for more details.

        wsgi.py
    """
    from . import app

    application = app


Running in Development mode ``run.py``

.. code:: python

    # -*- coding: utf-8 -*-
    """

        ~~~~~~~~~

        :author: nanang.jobs@gmail.com
        :copyright: (c) 2017 by Nanang Suryadi.
        :license: BSD, see LICENSE for more details.

        run.py.py
    """
    from . import app

    app.run(use_reloader=True)


Install
-------

.. code:: python

    pip install baka


Saran dan Kontribusi
--------------------

    Qoutes from heroes.

    “ Learning without thinking is useless, but thinking without learning is very dangerous! ”

    -― Sukarno, Di Bawah Bendera Revolusi : Jilid 1

    “ Apabila dalam diri seseorang masih ada rasa malu dan takut untuk berbuat suatu kebaikan, maka jaminan bagi orang tersebut adalah tidak akan bertemunya ia dengan kemajuan selangkah pun ”

    -- Sukarno

    “ Kurang cerdas dapat diperbaiki dengan belajar, kurang cakap dapat dihilangkan dengan pengalaman. Namun tidak jujur sulit diperbaiki. ”

    -- Bung Hatta

    “ Keberanian bukan berarti tidak takut, keberanian berarti menaklukan ketakutan. ”

    -- Bung Hatta
