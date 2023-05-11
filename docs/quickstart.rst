Quick Start
===========

.. currentmodule:: flask_session


Create your Flask application, load the configuration of choice, and
then create the :class:`Session` object by passing it the application.

The ``Session`` instance is not used for direct access, you should always use
:class:`flask.session`.

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

You may also set up your application later using :meth:`~Session.init_app`
method.

.. code-block:: python

    sess = Session()
    sess.init_app(app)
