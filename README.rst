Baka Framework
==============

`Baka Framework`_ adalah web application framework yang menggunakan core
wsgi dari Pyramid.

Penggunaan
----------

Kamu dapat menggunakan baka framework dengan sangat sederhana seperti
``route handler function``, misalnya.

.. code:: python


    from baka import Baka
    from baka.log import log

    app = Baka(__name__)

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

Modular Package/Folder
----------------------

Dengan penggunakan ``baka.include(callable)``, kamu dapat menggabungkan
module terpisah dari beberapa file didalam *package module*.

``contoh file: testbaka/view_user.py``

.. code:: python


    from .app import app


    @app.route('/users')
    def user(req):
        return {'users': 'all data'}

    def includeme(config):
        pass

``file: testbaka/app.py``

.. code:: python


    from baka import Baka
    from baka.log import log


    app = Baka(__name__)
    app.include('testbaka.view_user') # include module dari file view_user.py


    @app.route('/')
    def index_page(req):
        log.info(req)
        return {'Baka': 'Hello World!'}


    @app.route('/home')
    def home_page(req):
        log.info(req)
        return {'Route': 'home'}


App Folder
---------

Untuk Struktur Application Folder ``optional``

.. code:: html

    - root
        - package (AppBaka)
            - config ``optional, Baka(__name__, config_schema=True)``
                - config.yaml # digunakan for baka default configuration
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


Running
-------

Development mode

.. code::

    python run.py


Production mode with Gunicorn

.. code::

    gunicorn -w 1 -b 0.0.0.0:5000 AppBaka.wsgi


Contoh Aplikasi
---------------

.. code::

    git clone https://github.com/baka-framework/baka.git

    cd examples

    python3 -m venv env

    source env/bin/active

    pip install baka

    python run.py


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
