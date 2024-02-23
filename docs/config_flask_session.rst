
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

.. py:data:: SESSION_KEY_PREFIX

   A prefix that is added before all session keys. This makes it easier to use the same backend storage server for different apps.
   
   Default: ``'session:'``

.. py:data:: SESSION_ID_LENGTH

   The length of the session identifier in bytes (of entropy).
   
   Default: ``32``

.. py:data:: SESSION_SERIALIZATION_FORMAT
   
   The serialization format to use. Can be 'msgpack' or 'json'. Set to 'msgpack' for a more efficient serialization format. Set to 'json' for a human-readable format.
   
   Default: ``'msgpack'``

.. versionadded:: 0.7.0
    ``SESSION_SERIALIZATION_FORMAT``

.. versionadded:: 0.6
    ``SESSION_ID_LENGTH``
