import ast
import re
import docutils

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

NAME = 'baka'
DESC = 'Baka framework built top pyramid'
AUTHOR = 'Nanang Suryadi'
AUTHOR_EMAIL = 'nanang.ask@gmail.com'
URL = 'https://github.com/baka-framework/baka.git'
LICENSE = 'BSD License'
KEYWORDS = ['baka', 'framework', 'pyramid']
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Framework :: Pyramid',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
INSTALL_REQUIRES = [
    'setuptools>=27',
    'pyramid>=1.9',
    'werkzeug>=0.12',
    'bson',
    'trafaret>=0.12.1.dev0',
    'trafaret_config>=1.0.1'
]

dev_extras = [
    'nose',
    'nose-parameterized',
    'nosexcover',
    'coverage',
    'mock',
    'webtest',
    'pyramid',
    'baka',

    'readme',
    'twine',
]

EXTRAS_REQUIRE = {
    'dev': dev_extras,
    'docs': ['Sphinx'],
    'test': ['coverage'],
}
ENTRY_POINTS = """
      """

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('baka/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(name=NAME,
      version=version,
      description=DESC,
      long_description=long_description,
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      license=LICENSE,
      include_package_data=True,
      dependency_links=['https://github.com/baka-framework/baka.git/tree/master#egg=baka'],
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      entry_points=ENTRY_POINTS,
      packages=find_packages(include=['baka', 'baka.*']),
      zip_safe=False)
