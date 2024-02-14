Configuration example
---------------------

Here is an example of how to configure a redis backend:

.. code-block:: python

    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = Redis.from_url('redis://127.0.0.1:6379')

We are not supplying something like ``SESSION_REDIS_HOST`` and
``SESSION_REDIS_PORT``, if you want to use the ``RedisSessionInterface``,
you should configure ``SESSION_REDIS`` to your own ``redis.Redis`` instance.
This gives you more flexibility, such as using the same
``redis.Redis`` instance for cache purposes too, then you do not need to keep
two ``redis.Redis`` instance in the same process.

If you do not set ``SESSION_REDIS``, Flask-Session will assume you are developing locally and create a
``redis.Redis`` instance for you. It is expected you supply an instance of
``redis.Redis`` in production.

.. note::

    By default, sessions in Flask-Session are permanent with an expiration of 31 days.