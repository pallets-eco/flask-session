Usage
===========

Quickstart
-----------

.. currentmodule:: flask_session


Create your Flask application, load the configuration of choice, and
then create the :class:`Session` object by passing it the application.

.. note::

        You can not use ``Session`` instance directly, what ``Session`` does
        is just change the :attr:`~flask.Flask.session_interface` attribute on
        your Flask applications. You should always use :class:`flask.session` when accessing the current session.

.. code-block:: python

    from flask import Flask, session
    from flask_session import Session

    app = Flask(__name__)

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

This would automatically setup a redis client connected to `localhost:6379` and use it to store the session data.

See the `configuration section <config.rst>`_ for more details.

Alternative initialization
---------------------------

Rather than calling `Session(app)`, you may initialize later using :meth:`~Session.init_app`.

.. code-block:: python
    
    sess = Session()
    sess.init_app(app)

Or, if you prefer to directly set parameters rather than using the configuration constants, you can initialize by setting the interface constructor directly to the :attr:`session_interface`.

.. code-block:: python

    from flask_session.implementations.redis import RedisSessionInterface

    ...

    redis = Redis(
        host='localhost',
        port=6379,
    )
    app.session_interface = RedisSessionInterface(
        client=redis,
    )