import ast
import re
from codecs import open

from setuptools import setup, find_packages

NAME = 'baka'
DESC = 'Baka framework built top pyramid'
AUTHOR = 'Nanang Suryadi'
AUTHOR_EMAIL = 'nanang.ask@gmail.com'
URL = 'https://github.com/baka-framework/baka.git'
LICENSE = 'GNU GPL License'
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
EXTRAS_REQUIRE = {
    'dev': ['check-manifest'],
    'test': ['coverage'],
}
ENTRY_POINTS = """
      """

with open('README.rst', encoding='utf-8') as fp:
    LONGDESC = fp.read()

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('baka/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(name=NAME,
      version=version,
      description=DESC,
      long_description=LONGDESC,
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
