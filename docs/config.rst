Configuration
=============

.. include:: config_example.rst

.. include:: config_nonpermanent.rst

.. include:: config_cleanup.rst

.. include:: config_exceptions.rst

.. include:: config_flask.rst


Flask-Session configuration values
----------------------------------

These are specific to Flask-Session.

.. py:data:: SESSION_TYPE

   Specifies which type of session interface to use. Built-in session types:

   - **redis**: RedisSessionInterface
   - **memcached**: MemcachedSessionInterface
   - **filesystem**: FileSystemSessionInterface (Deprecated in 0.7.0, will be removed in 1.0.0 in favor of CacheLibSessionInterface)
   - **cachelib**: CacheLibSessionInterface
   - **mongodb**: MongoDBSessionInterface
   - **sqlalchemy**: SqlAlchemySessionInterface

.. py:data:: SESSION_PERMANENT

   Whether use permanent session or not.
   
   Default: ``True``

.. py:data:: SESSION_USE_SIGNER

   Whether sign the session cookie sid or not, if set to ``True``, you have to set :attr:`flask.Flask.secret_key`.

   .. note::
       This feature is historical and generally only relevant if you are using client-side sessions ie. not Flask-Session. SESSION_ID_LENGTH provides the relevant entropy for session identifiers.
   
   Default: ``False``

   .. deprecated:: 0.7.0

.. py:data:: SESSION_KEY_PREFIX

   A prefix that is added before all session keys. This makes it easier to use the same backend storage server for different apps.
   
   Default: ``'session:'``

.. py:data:: SESSION_ID_LENGTH

   The length of the session identifier in bytes (of entropy).
   
   Default: ``32``

   .. versionadded:: 0.6.0

.. py:data:: SESSION_SERIALIZATION_FORMAT
   
   The serialization format to use. Can be `'msgpack'`` or `'json'`. Set to `'msgpack'`` for a more efficient serialization format. Set to `'json'`` for a human-readable format.
   
   Default: ``'msgpack'``

   .. versionadded:: 0.7.0

.. deprecated:: 0.7.0
    ``SESSION_USE_SIGNER``

.. versionadded:: 0.7.0
    ``SESSION_SERIALIZATION_FORMAT``

.. versionadded:: 0.6.0
    ``SESSION_ID_LENGTH``


Storage configuration
---------------------


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

   .. deprecated:: 0.7.0

.. py:data:: SESSION_FILE_THRESHOLD
    
   The maximum number of items the session stores before it starts deleting some.
   
   Default: ``500``

   .. deprecated:: 0.7.0

.. py:data:: SESSION_FILE_MODE
    
   The file mode wanted for the session files.
   
   Default: ``0600``

   .. deprecated:: 0.7.0

CacheLib
~~~~~~~~~~~~~~~~~~~~~~~
.. py:data:: SESSION_CACHELIB

   Any valid `cachelib backend <https://cachelib.readthedocs.io/en/stable/>`_. This allows you maximum flexibility in choosing the cache backend and it's configuration.
   
   The following would set a cache directory called "flask_session" and a threshold of 500 items before it starts deleting some.
   
   .. code-block:: python

      app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
   
   .. important::
   
      A ``default_timeout`` set in any of the ``CacheLib`` backends will be overrode by the ``PERMANENT_SESSION_LIFETIME`` when each stored session's expiry is set.
   
   Default: ``FileSystemCache`` in ``./flask_session`` directory.

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

.. py:data:: SESSION_CLEANUP_N_REQUESTS

   Only applicable to non-TTL backends.
   
   The average number of requests after which Flask-Session will perform a session cleanup. This involves removing all session data that is older than ``PERMANENT_SESSION_LIFETIME``. Using the app command ``flask session_cleanup`` instead is preferable.
   
   Default: ``None``

.. deprecated:: 0.7.0

   ``SESSION_FILE_DIR``, ``SESSION_FILE_THRESHOLD``, ``SESSION_FILE_MODE``. Use ``SESSION_CACHELIB`` instead.

.. versionadded:: 0.7.0
    ``SESSION_CLEANUP_N_REQUESTS``

.. versionadded:: 0.6.0
    ``SESSION_SQLALCHEMY_BIND_KEY``, ``SESSION_SQLALCHEMY_SCHEMA``, ``SESSION_SQLALCHEMY_SEQUENCE``
