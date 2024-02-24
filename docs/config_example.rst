Example
---------------------

Here is an example of how to configure a redis backend:

.. code-block:: python

    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = Redis.from_url('redis://127.0.0.1:6379')

We are not supplying something like ``SESSION_REDIS_HOST`` and
``SESSION_REDIS_PORT``, instead you should configure ``SESSION_REDIS`` to your own :meth:`redis.Redis` instance.
This gives you more flexibility, such as using the same instance for cache purposes too, then you do not need to keep
two instances in the same process.

If you do not set ``SESSION_REDIS``, Flask-Session will assume you are developing locally and create a
:meth:`redis.Redis` instance for you. It is expected you supply an instance of
:meth:`redis.Redis` in production.

.. note::

    By default, sessions in Flask-Session are permanent with an expiration of 31 days.