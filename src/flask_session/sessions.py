import secrets
import time
from abc import ABC

try:
    import cPickle as pickle
except ImportError:
    import pickle
import random
from datetime import datetime
from datetime import timedelta as TimeDelta
from typing import Any, Optional

from flask import Flask, Request, Response
from flask.sessions import SessionInterface as FlaskSessionInterface
from flask.sessions import SessionMixin
from itsdangerous import BadSignature, Signer, want_bytes
from werkzeug.datastructures import CallbackDict

from ._utils import retry_query
from .defaults import Defaults


def total_seconds(timedelta):
    return int(timedelta.total_seconds())


class ServerSideSession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""

    def __bool__(self) -> bool:
        return bool(dict(self)) and self.keys() != {"_permanent"}

    def __init__(
        self,
        initial: Optional[dict[str, Any]] = None,
        sid: Optional[str] = None,
        permanent: Optional[bool] = None,
    ):
        def on_update(self) -> None:
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        if permanent:
            self.permanent = permanent
        self.modified = False


class RedisSession(ServerSideSession):
    pass


class MemcachedSession(ServerSideSession):
    pass


class FileSystemSession(ServerSideSession):
    pass


class MongoDBSession(ServerSideSession):
    pass


class SqlAlchemySession(ServerSideSession):
    pass


class SessionInterface(FlaskSessionInterface):
    def _generate_sid(self, session_id_length: int) -> str:
        return secrets.token_urlsafe(session_id_length)

    def __get_signer(self, app: Flask) -> Signer:
        if not hasattr(app, "secret_key") or not app.secret_key:
            raise KeyError("SECRET_KEY must be set when SESSION_USE_SIGNER=True")
        return Signer(app.secret_key, salt="flask-session", key_derivation="hmac")

    def _unsign(self, app, sid: str) -> str:
        signer = self.__get_signer(app)
        sid_as_bytes = signer.unsign(sid)
        sid = sid_as_bytes.decode()
        return sid

    def _sign(self, app, sid: str) -> str:
        signer = self.__get_signer(app)
        sid_as_bytes = want_bytes(sid)
        return signer.sign(sid_as_bytes).decode("utf-8")

    def _get_store_id(self, sid: str) -> str:
        return self.key_prefix + sid


class ServerSideSessionInterface(SessionInterface, ABC):
    """Used to open a :class:`flask.sessions.ServerSideSessionInterface` instance."""

    session_class = ServerSideSession
    serializer = None
    ttl = True

    def __init__(
        self,
        app: Flask,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_SID_LENGTH,
        cleanup_n_requests: Optional[int] = Defaults.SESSION_CLEANUP_N_REQUESTS,
    ):
        self.app = app
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent
        self.sid_length = sid_length
        self.has_same_site_capability = hasattr(self, "get_cookie_samesite")
        self.cleanup_n_requests = cleanup_n_requests

        # Cleanup settings for non-TTL databases only
        if getattr(self, "ttl", None) is False:
            if self.cleanup_n_requests:
                self.app.before_request(self._cleanup_n_requests)
            else:
                self._register_cleanup_app_command()

    def save_session(
        self, app: Flask, session: ServerSideSession, response: Response
    ) -> None:
        if not self.should_set_cookie(app, session):
            return

        # Get the domain and path for the cookie from the app
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # Generate a prefixed session id
        store_id = self._get_store_id(session.sid)

        # If the session is empty, do not save it to the database or set a cookie
        if not session:
            # If the session was deleted (empty and modified), delete the saved session  from the database and tell the client to delete the cookie
            if session.modified:
                self._delete_session(store_id)
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        # Update existing or create new session in the database
        self._upsert_session(app.permanent_session_lifetime, session, store_id)

        # Set the browser cookie
        response.set_cookie(
            key=app.config["SESSION_COOKIE_NAME"],
            value=self._sign(app, session.sid) if self.use_signer else session.sid,
            expires=self.get_expiration_time(app, session),
            httponly=self.get_cookie_httponly(app),
            domain=self.get_cookie_domain(app),
            path=self.get_cookie_path(app),
            secure=self.get_cookie_secure(app),
            samesite=self.get_cookie_samesite(app)
            if self.has_same_site_capability
            else None,
        )

    def open_session(self, app: Flask, request: Request) -> ServerSideSession:
        # Get the session ID from the cookie
        sid = request.cookies.get(app.config["SESSION_COOKIE_NAME"])

        # If there's no session ID, generate a new one
        if not sid:
            sid = self._generate_sid(self.sid_length)
            return self.session_class(sid=sid, permanent=self.permanent)

        # If the session ID is signed, unsign it
        if self.use_signer:
            try:
                sid = self._unsign(app, sid)
            except BadSignature:
                sid = self._generate_sid(self.sid_length)
                return self.session_class(sid=sid, permanent=self.permanent)

        # Retrieve the session data from the database
        store_id = self._get_store_id(sid)
        saved_session_data = self._retrieve_session_data(store_id)

        # If the saved session exists, load the session data from the document
        if saved_session_data is not None:
            return self.session_class(saved_session_data, sid=sid)

        # If the saved session does not exist, create a new session
        sid = self._generate_sid(self.sid_length)
        return self.session_class(sid=sid, permanent=self.permanent)

    # CLEANUP METHODS FOR NON TTL DATABASES

    def _register_cleanup_app_command(self):
        """
        Register a custom Flask CLI command for cleaning up expired sessions.

        Run the command with `flask session_cleanup`. Run with a cron job
        or scheduler such as Heroku Scheduler to automatically clean up expired sessions.
        """

        @self.app.cli.command("session_cleanup")
        def session_cleanup():
            with self.app.app_context():
                self._delete_expired_sessions()

    def _cleanup_n_requests(self) -> None:
        """
        Delete expired sessions on average every N requests.

        This is less desirable than using the scheduled app command cleanup as it may
        slow down some requests but may be useful for rapid development.
        """
        if self.cleanup_n_requests and random.randint(0, self.cleanup_n_requests) == 0:
            self._delete_expired_sessions()

    # METHODS TO BE IMPLEMENTED BY SUBCLASSES

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        raise NotImplementedError()

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        raise NotImplementedError()

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        raise NotImplementedError()

    @retry_query()
    def _delete_expired_sessions(self) -> None:
        """Delete expired sessions from the backend storage. Only required for non-TTL databases."""
        pass


class RedisSessionInterface(ServerSideSessionInterface):
    """Uses the Redis key-value store as a session backend. (`redis-py` required)

    :param redis: A ``redis.Redis`` instance.
    :param key_prefix: A prefix that is added to all Redis store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    serializer = pickle
    session_class = RedisSession
    ttl = True

    def __init__(
        self,
        app: Flask,
        key_prefix: str,
        use_signer: bool,
        permanent: bool,
        sid_length: int,
        redis: Any = Defaults.SESSION_REDIS,
    ):
        if redis is None:
            from redis import Redis

            redis = Redis()
        self.redis = redis
        super().__init__(app, key_prefix, use_signer, permanent, sid_length)

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (value) from the database
        serialized_session_data = self.redis.get(store_id)
        if serialized_session_data:
            try:
                session_data = self.serializer.loads(serialized_session_data)
                return session_data
            except pickle.UnpicklingError:
                self.app.logger.error("Failed to unpickle session data", exc_info=True)
        return None

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        self.redis.delete(store_id)

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_time_to_live = total_seconds(session_lifetime)

        # Serialize the session data
        serialized_session_data = self.serializer.dumps(dict(session))

        # Update existing or create new session in the database
        self.redis.set(
            name=store_id,
            value=serialized_session_data,
            ex=storage_time_to_live,
        )


class MemcachedSessionInterface(ServerSideSessionInterface):
    """A Session interface that uses memcached as backend. (`pylibmc` or `python-memcached` or `pymemcache` required)

    :param client: A ``memcache.Client`` instance.
    :param key_prefix: A prefix that is added to all Memcached store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    serializer = pickle
    session_class = MemcachedSession
    ttl = True

    def __init__(
        self,
        app: Flask,
        key_prefix: str,
        use_signer: bool,
        permanent: bool,
        sid_length: int,
        client: Any = Defaults.SESSION_MEMCACHED,
    ):
        if client is None:
            client = self._get_preferred_memcache_client()
        self.client = client
        super().__init__(app, key_prefix, use_signer, permanent, sid_length)

    def _get_preferred_memcache_client(self):
        clients = [
            ("pylibmc", ["127.0.0.1:11211"]),
            ("memcache", ["127.0.0.1:11211"]),
            ("pymemcache.client.base", "127.0.0.1:11211"),
        ]

        for module_name, server in clients:
            try:
                module = __import__(module_name)
                ClientClass = module.Client
                return ClientClass(server)
            except ImportError:
                continue

        raise ImportError("No memcache module found")

    def _get_memcache_timeout(self, timeout: int) -> int:
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        if timeout > 2592000:  # 60*60*24*30, 30 days
            # Switch to absolute timestamps.
            timeout += int(time.time())
        return timeout

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (item) from the database
        serialized_session_data = self.client.get(store_id)
        if serialized_session_data:
            try:
                session_data = self.serializer.loads(serialized_session_data)
                return session_data
            except pickle.UnpicklingError:
                self.app.logger.error("Failed to unpickle session data", exc_info=True)
        return None

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        self.client.delete(store_id)

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_time_to_live = total_seconds(session_lifetime)

        # Serialize the session data
        serialized_session_data = self.serializer.dumps(dict(session))

        # Update existing or create new session in the database
        self.client.set(
            store_id,
            serialized_session_data,
            self._get_memcache_timeout(storage_time_to_live),
        )


class FileSystemSessionInterface(ServerSideSessionInterface):
    """Uses the :class:`cachelib.file.FileSystemCache` as a session backend.

    :param cache_dir: the directory where session files are stored.
    :param threshold: the maximum number of items the session stores before it
                      starts deleting some.
    :param mode: the file mode wanted for the session files, default 0600
    :param key_prefix: A prefix that is added to FileSystemCache store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    session_class = FileSystemSession
    serializer = None
    ttl = True

    def __init__(
        self,
        app: Flask,
        key_prefix: str,
        use_signer: bool,
        permanent: bool,
        sid_length: int,
        cache_dir: str = Defaults.SESSION_FILE_DIR,
        threshold: int = Defaults.SESSION_FILE_THRESHOLD,
        mode: int = Defaults.SESSION_FILE_MODE,
    ):
        from cachelib.file import FileSystemCache

        self.cache = FileSystemCache(cache_dir, threshold=threshold, mode=mode)
        super().__init__(app, key_prefix, use_signer, permanent, sid_length)

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (item) from the database
        return self.cache.get(store_id)

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        self.cache.delete(store_id)

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_time_to_live = total_seconds(session_lifetime)

        # Serialize the session data (or just cast into dictionary in this case)
        session_data = dict(session)

        # Update existing or create new session in the database
        self.cache.set(
            key=store_id,
            value=session_data,
            timeout=storage_time_to_live,
        )


class MongoDBSessionInterface(ServerSideSessionInterface):
    """A Session interface that uses mongodb as backend. (`pymongo` required)

    :param client: A ``pymongo.MongoClient`` instance.
    :param db: The database you want to use.
    :param collection: The collection you want to use.
    :param key_prefix: A prefix that is added to all MongoDB store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    serializer = pickle
    session_class = MongoDBSession
    ttl = True

    def __init__(
        self,
        app: Flask,
        key_prefix: str,
        use_signer: bool,
        permanent: bool,
        sid_length: int,
        client: Any = Defaults.SESSION_MONGODB,
        db: str = Defaults.SESSION_MONGODB_DB,
        collection: str = Defaults.SESSION_MONGODB_COLLECT,
    ):
        import pymongo

        if client is None:
            client = pymongo.MongoClient()

        self.client = client
        self.store = client[db][collection]
        self.use_deprecated_method = int(pymongo.version.split(".")[0]) < 4

        # Create a TTL index on the expiration time, so that mongo can automatically delete expired sessions
        self.store.create_index("expiration", expireAfterSeconds=0)

        super().__init__(app, key_prefix, use_signer, permanent, sid_length)

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (document) from the database
        document = self.store.find_one({"id": store_id})
        if document:
            serialized_session_data = want_bytes(document["val"])
            try:
                session_data = self.serializer.loads(serialized_session_data)
                return session_data
            except pickle.UnpicklingError:
                self.app.logger.error("Failed to unpickle session data", exc_info=True)
        return None

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        if self.use_deprecated_method:
            self.store.remove({"id": store_id})
        else:
            self.store.delete_one({"id": store_id})

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_expiration_datetime = datetime.utcnow() + session_lifetime

        # Serialize the session data
        serialized_session_data = self.serializer.dumps(dict(session))

        # Update existing or create new session in the database
        if self.use_deprecated_method:
            self.store.update(
                {"id": store_id},
                {
                    "id": store_id,
                    "val": serialized_session_data,
                    "expiration": storage_expiration_datetime,
                },
                True,
            )
        else:
            self.store.update_one(
                {"id": store_id},
                {
                    "$set": {
                        "id": store_id,
                        "val": serialized_session_data,
                        "expiration": storage_expiration_datetime,
                    }
                },
                True,
            )


class SqlAlchemySessionInterface(ServerSideSessionInterface):
    """Uses the Flask-SQLAlchemy from a flask app as a session backend.

    :param app: A Flask app instance.
    :param db: A Flask-SQLAlchemy instance.
    :param table: The table name you want to use.
    :param key_prefix: A prefix that is added to all store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param sequence: The sequence to use for the primary key if needed.
    :param schema: The db schema to use
    :param bind_key: The db bind key to use
    :param cleanup_n_requests: Delete expired sessions on average every N requests.

    .. versionadded:: 0.7
        The `cleanup_n_requests` parameter was added.

    .. versionadded:: 0.6
        The `sid_length`, `sequence`, `schema` and `bind_key` parameters were added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    serializer = pickle
    session_class = SqlAlchemySession
    ttl = False

    def __init__(
        self,
        app: Flask,
        key_prefix: str,
        use_signer: bool,
        permanent: bool,
        sid_length: int,
        db: Any = Defaults.SESSION_SQLALCHEMY,
        table: str = Defaults.SESSION_SQLALCHEMY_TABLE,
        sequence: Optional[str] = Defaults.SESSION_SQLALCHEMY_SEQUENCE,
        schema: Optional[str] = Defaults.SESSION_SQLALCHEMY_SCHEMA,
        bind_key: Optional[str] = Defaults.SESSION_SQLALCHEMY_BIND_KEY,
        cleanup_n_requests: Optional[int] = Defaults.SESSION_CLEANUP_N_REQUESTS,
    ):
        self.app = app
        if db is None:
            from flask_sqlalchemy import SQLAlchemy

            db = SQLAlchemy(app)
        self.db = db
        self.sequence = sequence
        self.schema = schema
        self.bind_key = bind_key
        super().__init__(
            app, key_prefix, use_signer, permanent, sid_length, cleanup_n_requests
        )

        # Create the Session database model
        class Session(self.db.Model):
            __tablename__ = table

            if self.schema is not None:
                __table_args__ = {"schema": self.schema, "keep_existing": True}
            else:
                __table_args__ = {"keep_existing": True}

            if self.bind_key is not None:
                __bind_key__ = self.bind_key

            # Set the database columns, support for id sequences
            if sequence:
                id = self.db.Column(
                    self.db.Integer, self.db.Sequence(sequence), primary_key=True
                )
            else:
                id = self.db.Column(self.db.Integer, primary_key=True)
            session_id = self.db.Column(self.db.String(255), unique=True)
            data = self.db.Column(self.db.LargeBinary)
            expiry = self.db.Column(self.db.DateTime)

            def __init__(self, session_id: str, data: Any, expiry: datetime):
                self.session_id = session_id
                self.data = data
                self.expiry = expiry

            def __repr__(self):
                return "<Session data %s>" % self.data

        with app.app_context():
            self.db.create_all()

        self.sql_session_model = Session

    @retry_query()
    def _delete_expired_sessions(self) -> None:
        try:
            self.db.session.query(self.sql_session_model).filter(
                self.sql_session_model.expiry <= datetime.utcnow()
            ).delete(synchronize_session=False)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (record) from the database
        record = self.sql_session_model.query.filter_by(session_id=store_id).first()

        # "Delete the session record if it is expired as SQL has no TTL ability
        if record and (record.expiry is None or record.expiry <= datetime.utcnow()):
            try:
                self.db.session.delete(record)
                self.db.session.commit()
            except Exception:
                self.db.session.rollback()
                raise
            record = None

        if record:
            serialized_session_data = want_bytes(record.data)
            try:
                session_data = self.serializer.loads(serialized_session_data)
                return session_data
            except pickle.UnpicklingError as e:
                self.app.logger.exception(
                    e, "Failed to unpickle session data", exc_info=True
                )
        return None

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        try:
            self.sql_session_model.query.filter_by(session_id=store_id).delete()
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_expiration_datetime = datetime.utcnow() + session_lifetime

        # Serialize session data
        serialized_session_data = self.serializer.dumps(dict(session))

        # Update existing or create new session in the database
        try:
            record = self.sql_session_model.query.filter_by(session_id=store_id).first()
            if record:
                record.data = serialized_session_data
                record.expiry = storage_expiration_datetime
            else:
                record = self.sql_session_model(
                    session_id=store_id,
                    data=serialized_session_data,
                    expiry=storage_expiration_datetime,
                )
                self.db.session.add(record)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise
