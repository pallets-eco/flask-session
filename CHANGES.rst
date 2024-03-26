0.8.0 - 2024-03-26
------------------

Added
~~~~~~~
-   Add DynamoDB session interface (`#214 <https://github.com/pallets-eco/flask-session/pull/214>`_).
-   Add ability to install client libraries for backends using optional dependencies (extras) (`#228 <https://github.com/pallets-eco/flask-session/pull/228>`_).

Fixed
~~~~~
-   Include prematurely removed ``cachelib`` dependency. Will be removed in 1.0.0 to be an optional dependency (`#223 <https://github.com/pallets-eco/flask-session/issues/223>`_).


0.7.0 - 2024-03-18
------------------

Changed
~~~~~~~~
-   Access session interfaces via subfolder, for example ``flask_session.redis.RedisSessionInterface`` (`2bc7df <https://github.com/pallets-eco/flask-session/commit/2bc7df1be7b8929e55cb25f13845caf0503630d8>`_).
-   Deprecate ``pickle`` in favor of ``msgspec``, which is configured with ``SESSION_SERIALIZATION_FORMAT`` to choose between ``'json'`` and ``'msgpack'``. All sessions will convert to msgspec upon first interaction with 0.7.0. Pickle is still available to read existing sessions, but will be removed in 1.0.0. (`c7f8ce <https://github.com/pallets-eco/flask-session/commit/c7f8ced0e1532dea87850d34b3328a3fcb769988>`_, `c7f8ce <https://github.com/pallets-eco/flask-session/commit/c7f8ced0e1532dea87850d34b3328a3fcb769988>`_)
-   Deprecate ``SESSION_USE_SIGNER`` (`a5dba7 <https://github.com/pallets-eco/flask-session/commit/a5dba7022f806c8fb4412d0428b69dd4a077e4a7>`_).
-   Deprecate :class:`flask_session.filesystem.FileSystemSessionInterface` in favor of the broader :class:`flask_session.cachelib.CacheLibSessionInterface` (`2bc7df <https://github.com/pallets-eco/flask-session/commit/2bc7df1be7b8929e55cb25f13845caf0503630d8>`_).

Added
~~~~~~~
-   Add time-to-live expiration for MongoDB (`9acee3 <https://github.com/pallets-eco/flask-session/commit/9acee3c5fb7072476f3feea923529d19d5e855c3>`_).
-   Add retry for SQL based storage (`#211 <https://github.com/pallets-eco/flask-session/pull/211>`_).
-   Add ``flask session_cleanup`` command and alternatively, ``SESSION_CLEANUP_N_REQUESTS`` for SQLAlchemy or future non-TTL backends (`#211 <https://github.com/pallets-eco/flask-session/pull/211>`_).
-   Add type hints (`7d7d58 <https://github.com/pallets-eco/flask-session/commit/7d7d58ce371553da39095a421445cf639a62bd5f>`_).
-   Add logo and additional documentation.
-   Add vary cookie header when session modified or accessed as per flask's built-in session (`7ab698 <https://github.com/pallets-eco/flask-session/commit/7ab6980c8ba15912df13dd1e78242803e8104dd6>`_).
-   Add regenerate method to session interface to mitigate fixation (`#27 <https://github.com/pallets-eco/flask-session/pull/27>`_, `#39 <https://github.com/pallets-eco/flask-session/issues/39>`_)(`80df63 <https://github.com/pallets-eco/flask-session/commit/80df635ffd466fa7798f6031be5469b4d5dae069>`_).

Removed
~~~~~~~~~~
-   Remove null session in favour of relevant exception messages (`#107 <https://github.com/pallets-eco/flask-session/issues/107>`_, `#182 <https://github.com/pallets-eco/flask-session/issues/182>`_)(`d7ed1c <https://github.com/pallets-eco/flask-session/commit/d7ed1c6e7eb3904888b72f0d6c006db1b9b60795>`_).
-   Drop support for Python 3.7 which is end-of-life and precludes use of msgspec (`bd7e5b <https://github.com/pallets-eco/flask-session/commit/bd7e5b0bbfc10cdfa9c83b859593c69cc4381571>`_).

Fixed
~~~~~
-   Prevent session identifier reuse on storage miss (`#76 <https://github.com/pallets-eco/flask-session/pull/76>`_).
-   Abstraction to improve consistency between backends.
-   Enforce ``PERMANENT_SESSION_LIFETIME`` as expiration consistently for all backends (`#81 <https://github.com/pallets-eco/flask-session/issues/81>`_)(`86895b <https://github.com/pallets-eco/flask-session/commit/86895b523203ca67c9f87416bdbf028852dcb357>`_).
-   Specifically include backend session interfaces in public API and document usage (`#210 <https://github.com/pallets-eco/flask-session/issues/210>`_).
-   Fix non-permanent sessions not updating expiry (`#221 <https://github.com/pallets-eco/flask-session/issues/221>`_).


0.6.0 - 2024-01-16
------------------

Changed
~~~~~~~~

-   Use :meth:`~ServerSideSession.should_set_cookie` for preventing each request from saving the session again.
-   Do not store a permanent session that is otherwise empty.
-   Use `secrets` module to generate session identifiers, with 256 bits of entropy (was previously 122).
-   Explicitly name support for ``python-memcached``, ``pylibmc`` and ``pymemcache`` for ``cachelib`` backend.

Added
~~~~~~~

-   Introduce ``SESSION_KEY_LENGTH`` to control the length of the session key in bytes, default is 32.
-   Support SQLAlchemy ``SESSION_SQLALCHEMY_SEQUENCE``, ``SESSION_SQLALCHEMY_SCHEMA`` and ``SESSION_SQLALCHEMY_BINDKEY``

Removed
~~~~~~~~~~

-   Drop support for Redis < 2.6.12.

Fixed
~~~~~

-   Fix pymongo 4.0 compatibility.
-   Fix expiry is None bug in SQLAlchemy.
-   Fix bug when existing SQLAlchemy db instance.
-   Fix empty sessions being saved.
-   Support Flask 3.0 and Werkzeug 3.0


0.5.0 - 2023-05-11
-------------------

-   Drop support for Python < 3.7.
-   Switch to ``pyproject.toml`` and Flit for packaging.
-   Move to Pallets Community Ecosystem for community-driven maintenance.
-   Replace use of ``session_cookie_name`` for Flask 2.3 compatibility.


0.4.1
-------------

-   Temporarily pin Flask < 2.3.


0.4.0
-------------

-   Added support for ``SESSION_COOKIE_SAMESITE``.


0.3.2
-------------

-   Changed ``werkzeug.contrib.cache`` to ``cachelib``.


0.3.1
-------------

-   ``SqlAlchemySessionInterface`` is using ``VARCHAR(255)`` to store session id now.
-   ``SqlAlchemySessionInterface`` won't run `db.create_all` anymore.


0.3
-----------

-   ``SqlAlchemySessionInterface`` is using ``LargeBinary`` type to store data now.
-   Fixed ``MongoDBSessionInterface`` ``delete`` method not found.
-   Fixed ``TypeError`` when getting ``store_id`` using a signer.


0.2.3
-------------

-   Fixed signing failure in Python 3.
-   Fixed ``MongoDBSessionInterface`` failure in Python 3.
-   Fixed ``SqlAlchemySessionInterface`` failure in Python 3.
-   Fixed ``StrictRedis`` support.


0.2.2
-------------

-   Added support for non-permanent session.


0.2.1
-------------

-   Fixed signing failure.


0.2
-----------

-   Added ``SqlAlchemySessionInterface``.
-   Added support for cookie session id signing.
-   Various bugfixes.


0.1.1
-------------

-   Fixed MongoDB backend ``InvalidDocument`` error.


0.1
-----------

-   First public preview release.
