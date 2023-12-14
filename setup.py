"""
Flask-Server-Session
=============

Flask-Server-Session is an extension for Flask that adds
support for server-sided-sessions to your application.
"""
from setuptools import setup


setup(
    name='Flask-Server-Session',
    version='0.1.0',
    url='https://github.com/zachlagden/flask-session',
    license='MIT',
    author='Zach Lagden',
    author_email='contact@zachlagden.uk',
    description='Adds support for server-sided-sessions to your application',
    long_description=__doc__,
    packages=['flask_server_session'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=3.0.0',
        'cachelib'
    ],
    test_suite='test_server_session',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
