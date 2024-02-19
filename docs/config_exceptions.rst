Exception handling
-------------------

Flask-session will retry up to 3 times any database operation that fails with an Exception. This is to handle transient errors like network issues or database restarts. If the operation still fails after 3 retries, the exception will be raised.

If you want to show user more helpful error messages, you can use `Flask's error handling`_. For example:

.. code-block:: python

    @app.errorhandler(RedisError)
    def handle_redis_error(error):
        app.logger.error(f"Redis error encountered: {error}")
        return "A problem occurred with our Redis service. Please try again later.", 500


.. _Flask's error handling: https://flask.palletsprojects.com/en/3.0.x/errorhandling/