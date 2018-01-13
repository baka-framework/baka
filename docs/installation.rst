.. _installation:

Installation
============

Python Version
--------------

Kita merekomendasikan menggunakan versi Python 3 yang terbaru. Baka supports Python 3.4
dan terbaru, Python 2.7, dan PyPy.

Dependencies
------------

These distributions will be installed automatically when installing Baka.

* `Werkzeug`_ implements WSGI, the standard Python interface between
  applications and servers.
* `Pyramid`_ is a web framework python.


.. _Pyramid: https://trypyramid.com/
.. _Werkzeug: http://werkzeug.pocoo.org/

Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

These distributions will not be installed automatically. Baka will detect and
use them if you install them.

Virtual environments
--------------------

Use a virtual environment to manage the dependencies for your project, both in
development and in production.

What problem does a virtual environment solve? The more Python projects you
have, the more likely it is that you need to work with different versions of
Python libraries, or even Python itself. Newer versions of libraries for one
project can break compatibility in another project.

Virtual environments are independent groups of Python libraries, one for each
project. Packages installed for one project will not affect other projects or
the operating system's packages.

Python 3 comes bundled with the :mod:`venv` module to create virtual
environments. If you're using a modern version of Python, you can continue on
to the next section.

If you're using Python 2, see :ref:`install-install-virtualenv` first.

.. _install-create-env:

Create an environment
~~~~~~~~~~~~~~~~~~~~~

Create a project folder and a :file:`venv` folder within:

.. code-block:: sh

    mkdir myproject
    cd myproject
    python3 -m venv venv

On Windows:

.. code-block:: bat

    py -3 -m venv venv

If you needed to install virtualenv because you are on an older version of
Python, use the following command instead:

.. code-block:: sh

    virtualenv venv

On Windows:

.. code-block:: bat

    \Python27\Scripts\virtualenv.exe venv

Activate the environment
~~~~~~~~~~~~~~~~~~~~~~~~

Before you work on your project, activate the corresponding environment:

.. code-block:: sh

    . venv/bin/activate

On Windows:

.. code-block:: bat

    venv\Scripts\activate

Your shell prompt will change to show the name of the activated environment.

Install Baka
-------------

Within the activated environment, use the following command to install Baka:

.. code-block:: sh

    pip install Baka


.. _install-install-virtualenv:

Install virtualenv
------------------

If you are using Python 2, the venv module is not available. Instead,
install `virtualenv`_.

On Linux, virtualenv is provided by your package manager:

.. code-block:: sh

    # Debian, Ubuntu
    sudo apt-get install python-virtualenv

    # CentOS, Fedora
    sudo yum install python-virtualenv

    # Arch
    sudo pacman -S python-virtualenv

If you are on Mac OS X or Windows, download `get-pip.py`_, then:

.. code-block:: sh

    sudo python2 Downloads/get-pip.py
    sudo python2 -m pip install virtualenv

On Windows, as an administrator:

.. code-block:: bat

    \Python27\python.exe Downloads\get-pip.py
    \Python27\python.exe -m pip install virtualenv

Now you can continue to :ref:`install-create-env`.

.. _virtualenv: https://virtualenv.pypa.io/
.. _get-pip.py: https://bootstrap.pypa.io/get-pip.py