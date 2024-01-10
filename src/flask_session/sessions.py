import time
from abc import ABC
from datetime import datetime
import secrets

try:
    import cPickle as pickle
except ImportError:
    import pickle

from flask.sessions import SessionInterface as FlaskSessionInterface
from flask.sessions import SessionMixin
from werkzeug.datastructures import CallbackDict
from itsdangerous import Signer, BadSignature, want_bytes


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
    """Used to open a :class:`flask.sessions.NullSession` instance."""

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
        if self.use_signer:
            session_id = self._sign(app, session.sid)
        else:
            session_id = session.sid

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
        return self.fetch_session_sid(sid)

    def fetch_session_sid(self, sid):
        raise NotImplementedError()


class RedisSessionInterface(ServerSideSessionInterface):
    """Uses the Redis key-value store as a session backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param redis: A ``redis.Redis`` instance.
    :param key_prefix: A prefix that is added to all Redis store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    """

    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis, key_prefix, use_signer, permanent, sid_length):
        if redis is None:
            from redis import Redis

            redis = Redis()
        self.redis = redis
        super().__init__(redis, key_prefix, use_signer, permanent, sid_length)

    def fetch_session_sid(self, sid):
        if not isinstance(sid, str):
            sid = sid.decode("utf-8", "strict")
        val = self.redis.get(self.key_prefix + sid)
        if val is not None:
            try:
                data = self.serializer.loads(val)
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        if not self.should_set_cookie(app, session):
            return

        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                self.redis.delete(self.key_prefix + session.sid)
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.set(
            name=self.key_prefix + session.sid,
            value=val,
            ex=total_seconds(app.permanent_session_lifetime),
        )

        self.set_cookie_to_response(app, session, response, expires)


class MemcachedSessionInterface(ServerSideSessionInterface):
    """A Session interface that uses memcached as backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param client: A ``memcache.Client`` instance.
    :param key_prefix: A prefix that is added to all Memcached store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    """

    serializer = pickle
    session_class = MemcachedSession

    def __init__(self, client, key_prefix, use_signer, permanent, sid_length):
        if client is None:
            client = self._get_preferred_memcache_client()
            if client is None:
                raise RuntimeError("no memcache module found")
        self.client = client
        super().__init__(client, key_prefix, use_signer, permanent, sid_length)

    def _get_preferred_memcache_client(self):
        servers = ["127.0.0.1:11211"]
        try:
            import pylibmc
        except ImportError:
            pass
        else:
            return pylibmc.Client(servers)

        try:
            import memcache
        except ImportError:
            pass
        else:
            return memcache.Client(servers)

    def _get_memcache_timeout(self, timeout):
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        if timeout > 2592000:  # 60*60*24*30, 30 days
            # See http://code.google.com/p/memcached/wiki/FAQ
            # "You can set expire times up to 30 days in the future. After that
            # memcached interprets it as a date, and will expire the item after
            # said date. This is a simple (but obscure) mechanic."
            #
            # This means that we have to switch to absolute timestamps.
            timeout += int(time.time())
        return timeout

    def fetch_session_sid(self, sid):
        full_session_key = self.key_prefix + sid
        val = self.client.get(full_session_key)
        if val is not None:
            try:
                val = want_bytes(val)
                data = self.serializer.loads(val)
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        if not self.should_set_cookie(app, session):
            return
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        full_session_key = self.key_prefix + session.sid
        if not session:
            if session.modified:
                self.client.delete(full_session_key)
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session), 0)
        self.client.set(
            full_session_key,
            val,
            self._get_memcache_timeout(total_seconds(app.permanent_session_lifetime)),
        )

        self.set_cookie_to_response(app, session, response, expires)


class FileSystemSessionInterface(ServerSideSessionInterface):
    """Uses the :class:`cachelib.file.FileSystemCache` as a session backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param cache_dir: the directory where session files are stored.
    :param threshold: the maximum number of items the session stores before it
                      starts deleting some.
    :param mode: the file mode wanted for the session files, default 0600
    :param key_prefix: A prefix that is added to FileSystemCache store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
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

    def fetch_session_sid(self, sid):
        data = self.cache.get(self.key_prefix + sid)
        if data is not None:
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        if not self.should_set_cookie(app, session):
            return
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                self.cache.delete(self.key_prefix + session.sid)
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        expires = self.get_expiration_time(app, session)
        data = dict(session)
        self.cache.set(
            self.key_prefix + session.sid,
            data,
            total_seconds(app.permanent_session_lifetime),
        )
        self.set_cookie_to_response(app, session, response, expires)


class MongoDBSessionInterface(ServerSideSessionInterface):
    """A Session interface that uses mongodb as backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param client: A ``pymongo.MongoClient`` instance.
    :param db: The database you want to use.
    :param collection: The collection you want to use.
    :param key_prefix: A prefix that is added to all MongoDB store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    """

    serializer = pickle
    session_class = MongoDBSession

    def __init__(
        self,
        client,
        db,
        collection,
        tz_aware,
        key_prefix,
        use_signer,
        permanent,
        sid_length,
    ):
        import pymongo

        # Ensure that the client exists, support for tz_aware MongoClient
        if client is None:
            if tz_aware:
                client = pymongo.MongoClient(tz_aware=tz_aware)
            else:
                client = pymongo.MongoClient()

        self.client = client
        self.store = client[db][collection]
        self.tz_aware = tz_aware
        self.use_deprecated_method = int(pymongo.version.split(".")[0]) < 4
        super().__init__(self.store, key_prefix, use_signer, permanent, sid_length)

    def fetch_session_sid(self, sid):
        # Get the session document from the database
        prefixed_session_id = self.key_prefix + sid
        document = self.store.find_one({"id": prefixed_session_id})

        # Workaround for tz_aware MongoClient
        if self.tz_aware:
            utc_now = datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        else:
            utc_now = datetime.utcnow()

        # If the expiration time is less than or equal to the current time (expired), delete the document
        if document:
            expiration = document.get("expiration")
            if expiration is not None and expiration <= utc_now:
                if self.use_deprecated_method:
                    self.store.remove({"id": prefixed_session_id})
                else:
                    self.store.delete_one({"id": prefixed_session_id})
                document = None

        # If the session document still exists after checking for expiration, load the session data from the document
        if document is not None:
            try:
                val = document["val"]
                data = self.serializer.loads(want_bytes(val))
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid, permanent=self.permanent)

        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        if not self.should_set_cookie(app, session):
            return

        # Get the domain and path for the cookie from the app
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # Generate a prefixed session id from the session id as a storage key
        prefixed_session_id = self.key_prefix + session.sid

        # If the session is empty, do not save it to the database or set a cookie
        if not session:
            # If the session was deleted (empty and modified), delete the session document from the database and tell the client to delete the cookie
            if session.modified:
                if self.use_deprecated_method:
                    self.store.remove({"id": prefixed_session_id})
                else:
                    self.store.delete_one({"id": prefixed_session_id})
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        expires = self.get_expiration_time(app, session)
        value = self.serializer.dumps(dict(session))
        if self.use_deprecated_method:
            self.store.update(
                {"id": prefixed_session_id},
                {"id": prefixed_session_id, "val": value, "expiration": expires},
                True,
            )
        else:
            self.store.update_one(
                {"id": prefixed_session_id},
                {
                    "$set": {
                        "id": prefixed_session_id,
                        "val": value,
                        "expiration": expires,
                    }
                },
                True,
            )
        self.set_cookie_to_response(app, session, response, expires)


class SqlAlchemySessionInterface(ServerSideSessionInterface):
    """Uses the Flask-SQLAlchemy from a flask app as a session backend.

    .. versionadded:: 0.2

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

    def fetch_session_sid(self, sid):
        # Get the session document from the database
        store_id = self.key_prefix + sid
        saved_session = self.sql_session_model.query.filter_by(
            session_id=store_id
        ).first()

        # If the expiration time is less than or equal to the current time (expired), delete the document
        if saved_session and (
            not saved_session.expiry or saved_session.expiry <= datetime.utcnow()
        ):
            self.db.session.delete(saved_session)
            self.db.session.commit()
            saved_session = None

        # If the session document still exists after checking for expiration, load the session data from the document
        if saved_session:
            try:
                val = saved_session.data
                data = self.serializer.loads(want_bytes(val))
                return self.session_class(data, sid=sid)
            except:
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
            # If the session was deleted (empty and modified), delete the session document from the database and tell the client to delete the cookie
            if session.modified:
                self.sql_session_model.query.filter_by(
                    session_id=prefixed_session_id
                ).delete()
                self.db.session.commit()
                response.delete_cookie(
                    app.config["SESSION_COOKIE_NAME"], domain=domain, path=path
                )
            return

        # Serialize session data and get expiration time
        val = self.serializer.dumps(dict(session))
        expires = self.get_expiration_time(app, session)

        # Update or create the session in the database
        saved_session = self.sql_session_model.query.filter_by(
            session_id=prefixed_session_id
        ).first()
        if saved_session:
            saved_session.data = val
            saved_session.expiry = expires
        else:
            saved_session = self.sql_session_model(
                session_id=prefixed_session_id, data=val, expiry=expires
            )
            self.db.session.add(saved_session)

        # Commit changes and set the cookie
        self.db.session.commit()
        self.set_cookie_to_response(app, session, response, expires)
