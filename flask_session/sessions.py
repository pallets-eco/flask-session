"""
    flask_session.sessions
    ~~~~~~~~~~~~~~~~~~~~~~

    Server-side Sessions and SessionInterfaces.

    :copyright: (c) 2014 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""
import logging
from datetime import datetime
from uuid import uuid4


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
    def _generate_sid(self):
        return str(uuid4())

    def _get_signer(self, app):
        if not app.secret_key:
            return None
        return Signer(app.secret_key, salt="flask-session", key_derivation="hmac")


class NullSessionInterface(SessionInterface):
    """Used to open a :class:`flask.sessions.NullSession` instance."""

    def open_session(self, app, request):
        return None


class CachelibSessionInterface(SessionInterface):
    """Uses any class in `cachelib` as a session backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param cache: any class implements cachelib.BaseCache
    :param threshold: the maximum number of items the session stores before it
                      starts deleting some.
    :param mode: the file mode wanted for the session files, default 0600
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    session_class = ServerSideSession

    def __init__(self, cache, use_signer=False, permanent=True):
        self.cache = cache
        self.use_signer = use_signer
        self.permanent = permanent
        self.has_same_site_capability = hasattr(self, "get_cookie_samesite")

    def open_session(self, app, request):
        sid = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid, permanent=self.permanent)
        if self.use_signer:
            signer = self._get_signer(app)
            if signer is None:
                return None
            try:
                sid_as_bytes = signer.unsign(sid)
                sid = sid_as_bytes.decode()
            except BadSignature:
                sid = self._generate_sid()
                return self.session_class(sid=sid, permanent=self.permanent)

        data = self.cache.get(sid)
        if data is not None:
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, permanent=self.permanent)

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
    """Uses the Redis key-value store as a session backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param redis: A ``redis.Redis`` instance.
    :param key_prefix: A prefix that is added to all Redis store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis, key_prefix, use_signer=False, permanent=True):
        if redis is None:
            from redis import Redis

            redis = Redis()
        from cachelib import RedisCache

        cache = RedisCache(host=redis, key_prefix=key_prefix)
        CachelibSessionInterface.__init__(
            self, cache=cache, use_signer=use_signer, permanent=permanent
        )


class MemcachedSessionInterface(CachelibSessionInterface):
    """A Session interface that uses memcached as backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param client: A ``memcache.Client`` instance.
    :param key_prefix: A prefix that is added to all Memcached store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    serializer = pickle
    session_class = MemcachedSession

    def __init__(self, client, key_prefix, use_signer=False, permanent=True):

        from cachelib import MemcachedCache

        cache = MemcachedCache(servers=client, key_prefix=key_prefix)
        CachelibSessionInterface.__init__(
            self, cache=cache, use_signer=use_signer, permanent=permanent
        )


class FileSystemSessionInterface(CachelibSessionInterface):
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
    """

    session_class = FileSystemSession

    def __init__(
        self, cache_dir, threshold, mode, key_prefix, use_signer=False, permanent=True
    ):
        from cachelib.file import FileSystemCache

        cache = FileSystemCache(
            cache_dir, key_prefix=key_prefix, threshold=threshold, mode=mode
        )
        CachelibSessionInterface.__init__(
            self, cache=cache, use_signer=use_signer, permanent=permanent
        )


class MongoDBSessionInterface(CachelibSessionInterface):
    """A Session interface that uses mongodb as backend.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.

    :param client: A ``pymongo.MongoClient`` instance.
    :param db: The database you want to use.
    :param collection: The collection you want to use.
    :param key_prefix: A prefix that is added to all MongoDB store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    serializer = pickle
    session_class = MongoDBSession

    def __init__(
        self, client, db, collection, key_prefix, use_signer=False, permanent=True
    ):
        from cachelib import MongoDbCache

        cache = MongoDbCache(
            client, db=db, collection=collection, key_prefix=key_prefix
        )
        CachelibSessionInterface.__init__(
            self, cache=cache, use_signer=use_signer, permanent=permanent
        )


class SqlAlchemySessionInterface(SessionInterface):
    """Uses the Flask-SQLAlchemy from a flask app as a session backend.

    .. versionadded:: 0.2

    :param app: A Flask app instance.
    :param db: A Flask-SQLAlchemy instance.
    :param table: The table name you want to use.
    :param key_prefix: A prefix that is added to all store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    serializer = pickle
    session_class = SqlAlchemySession

    def __init__(self, app, db, table, key_prefix, use_signer=False, permanent=True):
        if db is None:
            from flask_sqlalchemy import SQLAlchemy

            db = SQLAlchemy(app)
        self.db = db
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent
        self.has_same_site_capability = hasattr(self, "get_cookie_samesite")

        class Session(self.db.Model):
            __tablename__ = table

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

        # self.db.create_all()
        self.sql_session_model = Session

    def open_session(self, app, request):
        sid = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid, permanent=self.permanent)
        if self.use_signer:
            signer = self._get_signer(app)
            if signer is None:
                return None
            try:
                sid_as_bytes = signer.unsign(sid)
                sid = sid_as_bytes.decode()
            except BadSignature:
                sid = self._generate_sid()
                return self.session_class(sid=sid, permanent=self.permanent)

        store_id = self.key_prefix + sid
        saved_session = self.sql_session_model.query.filter_by(
            session_id=store_id
        ).first()
        if saved_session and saved_session.expiry <= datetime.utcnow():
            # Delete expired session
            self.db.session.delete(saved_session)
            self.db.session.commit()
            saved_session = None
        if saved_session:
            try:
                val = saved_session.data
                data = self.serializer.loads(want_bytes(val))
                return self.session_class(data, sid=sid)
            except Exception as exp:
                logging.exception(exp)
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        store_id = self.key_prefix + session.sid
        saved_session = self.sql_session_model.query.filter_by(
            session_id=store_id
        ).first()
        if not session:
            if session.modified:
                if saved_session:
                    self.db.session.delete(saved_session)
                    self.db.session.commit()
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
        val = self.serializer.dumps(dict(session))
        if saved_session:
            saved_session.data = val
            saved_session.expiry = expires
            self.db.session.commit()
        else:
            new_session = self.sql_session_model(store_id, val, expires)
            self.db.session.add(new_session)
            self.db.session.commit()
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
