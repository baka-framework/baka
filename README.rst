Baka Framework
==============

`Baka Framework <https://github.com/baka-framework/baka>`_. is Baka Framework is web application framework based on Pyramid.


Usage
-----

You can use these as base classes for declarative model definitions, e.g.

.. code:: python

    from baka import Baka, log


    app = Baka(__name__)


    @app.route('/')
    def index_page(req):
        log.info(req)
        return {'Baka': 'Hello World!'}


    @app.route('/home')
    def home_page(req):
        log.info(req)
        return {'Route': 'home'}

    app.scan()

    if __name__ == '__main__':
        app.run()


Include Module
--------------

using baka include, you can mixing separate module in any different file and module package.

.. code:: python

    ``in other file testbaka/view_user.py``
    from .app import app


    @app.route('/users')
    def user(req):
        return {'users': 'all data'}

    def includeme(config):
        config.scan()

    ``file testbaka/app.py``
    from baka import Baka, log


    app = Baka(__name__)
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

    if __name__ == '__main__':
        app.run()


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
