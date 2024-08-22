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

Similarly, if you use a high-availability setup for Redis using Sentinel you can use the following setup

.. code-block:: python

    from redis import Sentinel
    app.config['SESSION_TYPE'] = 'redissentinel'
    app.config['SESSION_REDIS_SENTINEL'] = Sentinel(
            [("127.0.0.1", 26379), ("127.0.0.1", 26380), ("127.0.0.1", 26381)],
        )

It is expected that you set ``SESSION_REDIS_SENTINEL`` to your own :meth:`redis.Sentinel` instance.
The name of the master set is obtained via the config ``SESSION_REDIS_SENTINEL_MASTER_SET`` which defaults to ``mymaster``.



.. note::

    By default, sessions in Flask-Session are permanent with an expiration of 31 days.