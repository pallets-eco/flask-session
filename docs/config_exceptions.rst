Retries
--------

Only for SQL based storage, upon an exception, Flask-Session will retry with backoff up to 3 times. If the operation still fails after 3 retries, the exception will be raised.

For other storage types, the retry logic is either included or can be configured in the client setup. Refer to the relevant client documentation for more information.

Redis example with retries on certain errors:

.. code-block:: python
    
    from redis.backoff import ExponentialBackoff
    from redis.retry import Retry
    from redis.client import Redis
    from redis.exceptions import (
        BusyLoadingError,
        ConnectionError,
        TimeoutError
    )
    ...

    retry = Retry(ExponentialBackoff(), 3)
    SESSION_REDIS = Redis(host='localhost', port=6379, retry=retry, retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])


Logging
-------------------

If you want to show user more helpful error messages, you can use `Flask's error handling`_. For example:

.. code-block:: python

    @app.errorhandler(RedisError)
    def handle_redis_error(error):
        app.logger.error(f"Redis error encountered: {error}")
        return "A problem occurred with our Redis service. Please try again later.", 500


.. _Flask's error handling: https://flask.palletsprojects.com/en/3.0.x/errorhandling/