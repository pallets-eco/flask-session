import secrets
import time
from abc import ABC

try:
    import cPickle as pickle
except ImportError:
    import pickle

from datetime import datetime

from flask.sessions import SessionInterface as FlaskSessionInterface
from flask.sessions import SessionMixin
from itsdangerous import BadSignature, Signer, want_bytes
from werkzeug.datastructures import CallbackDict


def total_seconds(td):
    return td.days * 60 * 60 * 24 + td.seconds


class ServerSideSession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""

    def __bool__(self) -> bool:
        return bool(dict(self)) and self.keys() != {"_permanent"}

    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
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
    def _generate_sid(self, session_id_length):
        return secrets.token_urlsafe(session_id_length)

    def __get_signer(self, app):
        if not hasattr(app, "secret_key") or not app.secret_key:
            raise KeyError("SECRET_KEY must be set when SESSION_USE_SIGNER=True")
        return Signer(app.secret_key, salt="flask-session", key_derivation="hmac")

    def _unsign(self, app, sid):
        signer = self.__get_signer(app)
        sid_as_bytes = signer.unsign(sid)
        sid = sid_as_bytes.decode()
        return sid

    def _sign(self, app, sid):
        signer = self.__get_signer(app)
        sid_as_bytes = want_bytes(sid)
        return signer.sign(sid_as_bytes).decode("utf-8")


class NullSessionInterface(SessionInterface):
    """Used to open a :class:`flask.sessions.NullSession` instance.

    If you do not configure a different ``SESSION_TYPE``, this will be used to
    generate nicer error messages.  Will allow read-only access to the empty
    session but fail on setting.
    """

    def open_session(self, app, request):
        return None


class ServerSideSessionInterface(SessionInterface, ABC):
    """Used to open a :class:`flask.sessions.ServerSideSessionInterface` instance."""

    def __init__(self, db, key_prefix, use_signer=False, permanent=True, sid_length=32):
        self.db = db
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent
        self.sid_length = sid_length
        self.has_same_site_capability = hasattr(self, "get_cookie_samesite")

    def set_cookie_to_response(self, app, session, response, expires):
        session_id = self._sign(app, session.sid) if self.use_signer else session.sid
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        samesite = None
        if self.has_same_site_capability:
            samesite = self.get_cookie_samesite(app)

        response.set_cookie(
            app.config["SESSION_COOKIE_NAME"],
            session_id,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            samesite=samesite,
        )

    def open_session(self, app, request):
        sid = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
        if not sid:
            sid = self._generate_sid(self.sid_length)
            return self.session_class(sid=sid, permanent=self.permanent)
        if self.use_signer:
            try:
                sid = self._unsign(app, sid)
            except BadSignature:
                sid = self._generate_sid(self.sid_length)
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.fetch_session(sid)

    def fetch_session(self, sid):
        raise NotImplementedError()


class CachelibSessionInterface(ServerSideSessionInterface):
    """Uses any class in `cachelib` as a session backend.

    :param cache: any class implements cachelib.BaseCache
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    session_class = ServerSideSession

    def __init__(self, cache, key_prefix, use_signer=False, permanent=True, sid_length=32):
        self.cache = cache
        super.__init__(None, key_prefix, use_signer, permanent, sid_length)

    def fetch_session(self, sid):
        self.cache.get(sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                self.cache.delete(session.sid)
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        conditional_cookie_kwargs = {}
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        if self.has_same_site_capability:
            conditional_cookie_kwargs["samesite"] = self.get_cookie_samesite(app)
        expires = self.get_expiration_time(app, session)
        data = dict(session)
        self.cache.set(session.sid, data, total_seconds(app.permanent_session_lifetime))
        if self.use_signer:
            session_id = self._get_signer(app).sign(want_bytes(session.sid))
        else:
            session_id = session.sid
        response.set_cookie(
            app.config["SESSION_COOKIE_NAME"],
            session_id,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            **conditional_cookie_kwargs
        )

class RedisSessionInterface(CachelibSessionInterface):
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

    def __init__(self, redis, key_prefix, use_signer, permanent, sid_length):
        if redis is None:
            from redis import Redis

            redis = Redis()
        self.redis = redis
        from cachelib import RedisCache

        cache = RedisCache(host=redis, key_prefix=key_prefix)
        super().__init__(cache, key_prefix, use_signer, permanent, sid_length)


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

    def __init__(self, client, key_prefix, use_signer, permanent, sid_length):
        if client is None:
            client = self._get_preferred_memcache_client()
        self.client = client
        super().__init__(client, key_prefix, use_signer, permanent, sid_length)

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

    def _get_memcache_timeout(self, timeout):
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        if timeout > 2592000:  # 60*60*24*30, 30 days
            # Switch to absolute timestamps.
            timeout += int(time.time())
        return timeout

    def fetch_session(self, sid):
        # Get the saved session (item) from the database
        prefixed_session_id = self.key_prefix + sid
        item = self.client.get(prefixed_session_id)

        # If the saved session still exists and hasn't auto-expired, load the session data from the document
        if item is not None:
            try:
                session_data = self.serializer.loads(want_bytes(item))
                return self.session_class(session_data, sid=sid)
            except pickle.UnpicklingError:
                return self.session_class(sid=sid, permanent=self.permanent)

        # If the saved session  does not exist, create a new session
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        if not self.should_set_cookie(app, session):
            return

        # Get the domain and path for the cookie from the app config
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # Generate a prefixed session id from the session id as a storage key
        prefixed_session_id = self.key_prefix + session.sid

        # If the session is empty, do not save it to the database or set a cookie
        if not session:
            # If the session was deleted (empty and modified), delete the saved session  from the database and tell the client to delete the cookie
            if session.modified:
                self.client.delete(prefixed_session_id)
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        # Get the new expiration time for the session
        expiration_datetime = self.get_expiration_time(app, session)

        # Serialize the session data
        serialized_session_data = self.serializer.dumps(dict(session))

        # Update existing or create new session in the database
        self.client.set(
            prefixed_session_id,
            serialized_session_data,
            self._get_memcache_timeout(total_seconds(app.permanent_session_lifetime)),
        )

        # Set the browser cookie
        self.set_cookie_to_response(app, session, response, expiration_datetime)


class FileSystemSessionInterface(CachelibSessionInterface):
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

    def __init__(
        self,
        cache_dir,
        threshold,
        mode,
        key_prefix,
        use_signer,
        permanent,
        sid_length,
    ):
        from cachelib.file import FileSystemCache

        self.cache = FileSystemCache(cache_dir, threshold=threshold, mode=mode)
        super().__init__(self.cache, key_prefix, use_signer, permanent, sid_length)



class MongoDBSessionInterface(CachelibSessionInterface):
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

    def __init__(
        self,
        client,
        db,
        collection,
        key_prefix,
        use_signer,
        permanent,
        sid_length,
    ):
        import pymongo

        if client is None:
            client = pymongo.MongoClient()

        from cachelib import MongoDbCache

        cache = MongoDbCache(
            client, db=db, collection=collection, key_prefix=key_prefix
        )
        super().__init__(cache, key_prefix, use_signer, permanent, sid_length)


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

    .. versionadded:: 0.6
        The `sid_length`, `sequence`, `schema` and `bind_key` parameters were added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    serializer = pickle
    session_class = SqlAlchemySession

    def __init__(
        self,
        app,
        db,
        table,
        sequence,
        schema,
        bind_key,
        key_prefix,
        use_signer,
        permanent,
        sid_length,
    ):
        if db is None:
            from flask_sqlalchemy import SQLAlchemy

            db = SQLAlchemy(app)

        self.db = db
        self.sequence = sequence
        self.schema = schema
        self.bind_key = bind_key
        super().__init__(self.db, key_prefix, use_signer, permanent, sid_length)

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

            def __init__(self, session_id, data, expiry):
                self.session_id = session_id
                self.data = data
                self.expiry = expiry

            def __repr__(self):
                return "<Session data %s>" % self.data

        with app.app_context():
            self.db.create_all()

        self.sql_session_model = Session

    def fetch_session(self, sid):
        # Get the saved session (record) from the database
        store_id = self.key_prefix + sid
        record = self.sql_session_model.query.filter_by(session_id=store_id).first()

        # If the expiration time is less than or equal to the current time (expired), delete the document
        if record is not None:
            expiration_datetime = record.expiry
            if expiration_datetime is None or expiration_datetime <= datetime.utcnow():
                self.db.session.delete(record)
                self.db.session.commit()
                record = None

        # If the saved session still exists after checking for expiration, load the session data from the document
        if record:
            try:
                session_data = self.serializer.loads(want_bytes(record.data))
                return self.session_class(session_data, sid=sid)
            except pickle.UnpicklingError:
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        if not self.should_set_cookie(app, session):
            return

        # Get the domain and path for the cookie from the app
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # Generate a prefixed session id
        prefixed_session_id = self.key_prefix + session.sid

        # If the session is empty, do not save it to the database or set a cookie
        if not session:
            # If the session was deleted (empty and modified), delete the saved session  from the database and tell the client to delete the cookie
            if session.modified:
                self.sql_session_model.query.filter_by(
                    session_id=prefixed_session_id
                ).delete()
                self.db.session.commit()
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        # Serialize session data
        serialized_session_data = self.serializer.dumps(dict(session))

        # Get the new expiration time for the session
        expiration_datetime = self.get_expiration_time(app, session)

        # Update existing or create new session in the database
        record = self.sql_session_model.query.filter_by(
            session_id=prefixed_session_id
        ).first()
        if record:
            record.data = serialized_session_data
            record.expiry = expiration_datetime
        else:
            record = self.sql_session_model(
                session_id=prefixed_session_id,
                data=serialized_session_data,
                expiry=expiration_datetime,
            )
            self.db.session.add(record)
        self.db.session.commit()

        # Set the browser cookie
        self.set_cookie_to_response(app, session, response, expiration_datetime)
