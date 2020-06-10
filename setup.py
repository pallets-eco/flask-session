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
from setuptools import setup


setup(
    name='Flask-Session',
    version='0.3.3',
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
        'flask-caching>=1.7,<2',  # It drops Python 2.7 support since 1.8
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
