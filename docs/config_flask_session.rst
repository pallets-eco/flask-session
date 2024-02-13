
Flask-Session configuration values
----------------------------------

These are specific to Flask-Session.

.. py:data:: SESSION_TYPE

   Specifies which type of session interface to use. Built-in session types:

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

   .. note::
       This feature is historical and generally only relevant if you are using client-side sessions ie. not Flask-Session. SESSION_ID_LENGTH provides the relevant entropy for session identifiers.
   
   Default: ``False``

.. py:data:: SESSION_KEY_PREFIX

   A prefix that is added before all session keys. This makes it easier to use the same backend storage server for different apps.
   
   Default: ``'session:'``

.. py:data:: SESSION_ID_LENGTH

   The length of the session identifier in bytes (of entropy).
   
   Default: ``32``

.. versionadded:: 0.6
    ``SESSION_ID_LENGTH``
