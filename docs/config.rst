Configuration
=============

Backend Configuration
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

    By default, all non-null sessions in Flask-Session are permanent.

Relevant Flask Configuration Values
-------------------------------------
The following configuration values are builtin configuration values within
Flask itself that are relate to the Flask session cookie set on the browser. Flask-Session
loads these values from your Flask application config, so you should configure
your app first before you pass it to Flask-Session.  

Note that these values
cannot be modified after the ``init_app`` was applied so make sure to not
modify them at runtime. 

``PERMANENT_SESSION_LIFETIME`` effects not only the browser cookie lifetime but also 
the expiration in the server side session storage.


.. py:data:: SESSION_COOKIE_NAME

   The name of the session cookie.

.. py:data:: SESSION_COOKIE_DOMAIN

   The domain for the session cookie. If this is not set, the cookie will be valid for all subdomains of ``SERVER_NAME``.

.. py:data:: SESSION_COOKIE_PATH

   The path for the session cookie. If this is not set the cookie will be valid for all of ``APPLICATION_ROOT`` or if that is not set for ``'/'``.

.. py:data:: SESSION_COOKIE_HTTPONLY

   Controls if the cookie should be set with the httponly flag.

   Default: ``True``

.. py:data:: SESSION_COOKIE_SECURE

   Controls if the cookie should be set with the secure flag. Browsers will only send cookies with requests over HTTPS if the cookie is marked "secure". The application must be served over HTTPS for this to make sense.

   Default: ``False``

.. py:data:: PERMANENT_SESSION_LIFETIME

   The lifetime of a permanent session as :class:`datetime.timedelta` object. Starting with Flask 0.8 this can also be an integer representing seconds.


Flask-Session Configuration Values
----------------------------------

.. py:data:: SESSION_TYPE

   Specifies which type of session interface to use. Built-in session types:

   - **null**: NullSessionInterface (default)
   - **redis**: RedisSessionInterface
   - **memcached**: MemcachedSessionInterface
   - **filesystem**: FileSystemSessionInterface
   - **mongodb**: MongoDBSessionInterface
   - **sqlalchemy**: SqlAlchemySessionInterface

.. py:data:: SESSION_PERMANENT

   Whether use permanent session or not.
   
   Default: ``True``

.. py:data:: SESSION_USE_SIGNER

   Whether sign the session cookie sid or not, if set to ``True``, you have to set :attr:`flask.Flask.secret_key`. 
   
   Default: ``False``

.. py:data:: SESSION_KEY_PREFIX

   A prefix that is added before all session keys. This makes it possible to use the same backend storage server for different apps.
   
   Default: ``'session:'``

.. py:data:: SESSION_ID_LENGTH

   The length of the session identifier in bytes (of entropy).
   
   Default: ``32``

.. versionadded:: 0.6
    ``SESSION_ID_LENGTH``

Backend-specific Configuration Values
---------------------------------------

Redis
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_REDIS

   A ``redis.Redis`` instance.
   
   Default: Instance connected to ``127.0.0.1:6379``


Memcached
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_MEMCACHED

   A ``memcache.Client`` instance.
   
   Default: Instance connected to ``127.0.0.1:6379``


FileSystem
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_FILE_DIR

   The directory where session files are stored.
   
   Default: ``flask_session`` directory under current working directory.

.. py:data:: SESSION_FILE_THRESHOLD
    
   The maximum number of items the session stores before it starts deleting some.
   
   Default: ``500``

.. py:data:: SESSION_FILE_MODE
    
   The file mode wanted for the session files.
   
   Default: ``0600``


MongoDB
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_MONGODB

   A ``pymongo.MongoClient`` instance.
   
   Default: Instance connected to ``127.0.0.1:27017``

.. py:data:: SESSION_MONGODB_DB
    
   The MongoDB database you want to use.
   
   Default: ``'flask_session'``

.. py:data:: SESSION_MONGODB_COLLECT
    
   The MongoDB collection you want to use.
   
   Default: ``'sessions'``


SqlAlchemy
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_SQLALCHEMY

   A ``flask_sqlalchemy.SQLAlchemy`` instance whose database connection URI is configured using the ``SQLALCHEMY_DATABASE_URI`` parameter.
   
   Must be set in flask_sqlalchemy version 3.0 or higher.

.. py:data:: SESSION_SQLALCHEMY_TABLE
    
   The name of the SQL table you want to use.
   
   Default: ``'sessions'``

.. py:data:: SESSION_SQLALCHEMY_SEQUENCE
    
   The name of the sequence you want to use for the primary key.
   
   Default: ``None``

.. py:data:: SESSION_SQLALCHEMY_SCHEMA
    
   The name of the schema you want to use.
   
   Default: ``None``

.. py:data:: SESSION_SQLALCHEMY_BIND_KEY
    
   The name of the bind key you want to use.
   
   Default: ``None``

.. versionadded:: 0.6
    ``SESSION_SQLALCHEMY_BIND_KEY``, ``SESSION_SQLALCHEMY_SCHEMA``, ``SESSION_SQLALCHEMY_SEQUENCE``
