Flask-Session
=============

.. module:: flask.ext.session

Welcome to Flask-Session's documentation.  Flask-Session is an extension for `Flask`_ that adds support for Server-side ``Session`` to your application.

.. _Flask: http://flask.pocoo.org/

If you are not familiar with Flask, I highly recommend you to give it a try.  Flask is a microframework for Python and it is really Fun to work with.  If you want to dive into its documentation, check out the following links:

-   `Flask Documentation <http://flask.pocoo.org/docs/>`_

Installation
------------

Install the extension with the following command::

    $ easy_install Flask-Session

or alternatively if you have pip installed::
    
    $ pip install Flask-Session

Quickstart
----------

Flask-Session is really easy to use.

Basically for the common use of having one Flask application all you have to do is to create your Flask application, load the configuration of choice and then create the :class:`Session` object by passing it the application.

The ``Session`` instance is not used for direct access, you should always use :class:`flask.session`::
    
    from flask import Flask, session
    from flask.ext.session import Session

    app = Flask(__name__)
    # Check Configuration section for more details
    app.config.from_object(__name__)
    Session(app)

    @app.route('/set/')
    def set():
        session['key'] = 'value'
        return 'ok'

    @app.route('/get/')
    def get():
        return session.get('key', 'not set')

You may also set up your application later using :meth:`~Session.init_app` method::
    
    sess = Session()
    sess.init_app(app)

Configuration
-------------

Configuration

API
---

.. autoclass:: Session
   :members: init_app

.. include:: ../CHANGES
