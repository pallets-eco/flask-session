Flask-Session
=============

Flask-Session is an extension for Flask that adds support for server-side sessions to
your application.

   
.. image:: https://github.com/pallets-eco/flask-session/actions/workflows/test.yaml/badge.svg?branch=development
    :target: https://github.com/pallets-eco/flask-session/actions/workflows/test.yaml?query=workflow%3ACI+branch%3Amain
    :alt: Tests

.. image:: https://readthedocs.org/projects/flask-session/badge/?version=stable&style=flat
    :target: https://flask-session.readthedocs.io
    :alt: docs

.. image:: https://img.shields.io/github/license/pallets-eco/flask-session
    :target: ./LICENSE
    :alt: BSD-3 Clause License

.. image:: https://img.shields.io/pypi/v/flask-session.svg?
    :target: https://pypi.org/project/flask-session
    :alt: PyPI

.. image:: https://img.shields.io/badge/dynamic/json?query=info.requires_python&label=python&url=https%3A%2F%2Fpypi.org%2Fpypi%2Fflask-session%2Fjson
    :target: https://pypi.org/project/Flask-Session/
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/github/v/release/pallets-eco/flask-session?include_prereleases&label=latest-prerelease
    :target: https://github.com/pallets-eco/flask-session/releases
    :alt: pre-release

.. image:: https://codecov.io/gh/pallets-eco/flask-session/branch/master/graph/badge.svg?token=yenl5fzxxr
    :target: https://codecov.io/gh/pallets-eco/flask-session
    :alt: codecov

.. image:: https://img.shields.io/discord/531221516914917387?logo=discord
    :target: https://discord.gg/pallets
    :alt: Discord

Installing
------------
Install and update using pip:

.. code-block:: bash

    $ pip install flask-session

A Simple Example
--------------------

.. code-block:: python

    from flask import Flask, session
    from flask_session import Session

    app = Flask(__name__)
    # Check Configuration section for more details
    SESSION_TYPE = 'redis'
    app.config.from_object(__name__)
    Session(app)

    @app.route('/set/')
    def set():
        session['key'] = 'value'
        return 'ok'

    @app.route('/get/')
    def get():
        return session.get('key', 'not set')

Documentation
-------------
Learn more at the official `Flask-Session Documentation <https://flask-session.readthedocs.io/en/latest/>`_.

Donate
--------
The Pallets organization develops and supports Flask-Session and other popular packages. In order to grow the community of contributors and users, and allow the maintainers to devote more time to the projects, please donate today.


