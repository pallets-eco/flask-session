Built-in Session Interfaces
===========================

.. currentmodule:: flask_session


:class:`NullSessionInterface`
-----------------------------

If you do not configure a different ``SESSION_TYPE``, this will be used to
generate nicer error messages.  Will allow read-only access to the empty
session but fail on setting.


:class:`RedisSessionInterface`
------------------------------

Uses the Redis key-value store as a session backend. (`redis-py`_ required)

Relevant configuration values:

- SESSION_REDIS


:class:`MemcachedSessionInterface`
----------------------------------

Uses the Memcached as a session backend. (`pylibmc`_ or `memcache`_ required)

- SESSION_MEMCACHED


:class:`FileSystemSessionInterface`
-----------------------------------

Uses the :class:`cachelib.file.FileSystemCache` as a session backend.

- SESSION_FILE_DIR
- SESSION_FILE_THRESHOLD
- SESSION_FILE_MODE


:class:`MongoDBSessionInterface`
--------------------------------

Uses the MongoDB as a session backend. (`pymongo`_ required)

- SESSION_MONGODB
- SESSION_MONGODB_DB
- SESSION_MONGODB_COLLECT

.. _redis-py: https://github.com/andymccurdy/redis-py
.. _pylibmc: http://sendapatch.se/projects/pylibmc/
.. _memcache: https://github.com/linsomniac/python-memcached
.. _pymongo: http://api.mongodb.org/python/current/index.html


:class:`SqlAlchemySessionInterface`
-----------------------------------

.. versionadded:: 0.2

Uses SQLAlchemy as a session backend. (`Flask-SQLAlchemy`_ required)

- SESSION_SQLALCHEMY
- SESSION_SQLALCHEMY_TABLE

.. _Flask-SQLAlchemy: https://pythonhosted.org/Flask-SQLAlchemy/
