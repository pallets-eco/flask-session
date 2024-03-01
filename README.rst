.. image:: https://raw.githubusercontent.com/pallets-eco/flask-session/development/docs/_static/icon/favicon-192x192.png
    :alt: Flask-Session
    :target: https://flask-session.readthedocs.io
    :align: left
    :width: 60px

==============
Flask-Session
==============

Flask-Session is an extension for Flask that adds support for server-side sessions to
your application.

.. image:: https://img.shields.io/github/actions/workflow/status/pallets-eco/flask-session/test.yaml?logo=github
    :alt: GitHub Actions Workflow Status
    :target: https://github.com/pallets-eco/flask-session/actions/workflows/test.yaml?query=workflow%3ACI+branch%3Adevelopment

.. image:: https://img.shields.io/readthedocs/flask-session?logo=readthedocs
    :target: https://flask-session.readthedocs.io
    :alt: Documentation status

.. image:: https://img.shields.io/github/license/pallets-eco/flask-session?logo=bsd
    :target: ./LICENSE
    :alt: BSD-3 Clause License

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&label=style
    :target: https://github.com/astral-sh/ruff
    :alt: Code style: ruff

.. image:: https://img.shields.io/pypi/v/flask-session.svg?logo=pypi
    :target: https://pypi.org/project/flask-session
    :alt: PyPI - Latest Version

.. image:: https://img.shields.io/badge/dynamic/json?query=info.requires_python&label=python&logo=python&url=https%3A%2F%2Fpypi.org%2Fpypi%2Fflask-session%2Fjson
    :target: https://pypi.org/project/Flask-Session/
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/discord/531221516914917387?logo=discord
    :target: https://discord.gg/pallets
    :alt: Discord

.. image:: https://img.shields.io/pypi/dm/flask-session?logo=pypi
    :target: https://pypistats.org/packages/flask-session
    :alt: PyPI - Downloads

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

Supported Storage Types
------------------------
- Redis
- Memcached
- FileSystem
- MongoDB
- SQLALchemy

Documentation
-------------
Learn more at the official `Flask-Session Documentation <https://flask-session.readthedocs.io/en/latest/>`_.

Donate
--------
The Pallets organization develops and supports Flask-Session and other popular packages. In order to grow the community of contributors and users, and allow the maintainers to devote more time to the projects, please donate today.


