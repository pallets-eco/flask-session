Usage
===========

Quickstart
-----------

.. currentmodule:: flask_session


Create your :class:`~flask.Flask` application, load the configuration of choice, and
then create the :class:`Session` object by passing it the application.

.. code-block:: python

    from flask import Flask, session
    from flask_session import Session

    app = Flask(__name__)

    SESSION_TYPE = 'redis'
    SESSION_REDIS = Redis(host='localhost', port=6379)
    app.config.from_object(__name__)
    Session(app)

    @app.route('/set/')
    def set():
        session['key'] = 'value'
        return 'ok'

    @app.route('/get/')
    def get():
        return session.get('key', 'not set')

See the configuration section for more details.

.. note::

    You can not use :class:`~Session` instance directly, what :class:`~Session` does
    is just change the :attr:`~flask.Flask.session_interface` attribute on
    your Flask applications. You should always use :class:`flask.session` when accessing or modifying the current session.


Alternative initialization
---------------------------

Rather than calling :class:`~Session`, you may initialize later using :meth:`~Session.init_app`.

.. code-block:: python
    
    ...
    sess = Session()
    sess.init_app(app)

Or, if you prefer to directly set parameters rather than using the configuration constants, you can initialize by setting an instance of :class:`flask_session.redis.RedisSessionInterface` directly to the :attr:`flask.Flask.session_interface`.

.. code-block:: python

    from flask import Flask, session
    from flask_session.redis import RedisSessionInterface
    from redis import Redis

    app = Flask(__name__)

    redis = Redis(host='localhost', port=6379)
    app.session_interface = RedisSessionInterface(client=redis)