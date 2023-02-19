"""
Flask-Session
-------------

Flask-Session is an extension for Flask that adds support for
Server-side Session to your application.

Links
`````

* `development version
  <https://github.com/fengsp/flask-session/zipball/master#egg=Flask-dev>`_

"""
import re, io
from setuptools import setup

# setup.py shall not import main package
__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open('flask_session/__init__.py', encoding='utf_8_sig').read()
    ).group(1)

setup(
    name='Flask-Session',
    version=__version__,
    url='https://github.com/fengsp/flask-session',
    license='BSD',
    author='Shipeng Feng',
    author_email='fsp261@gmail.com',
    description='Adds server-side session support to your Flask application',
    long_description=__doc__,
    packages=['flask_session'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
        'cachelib'
    ],
    test_suite='test_session',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
