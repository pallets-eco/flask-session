# -*- coding: utf-8 -*-
"""
    flaskext.session.sessions
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Server-side Sessions and SessionInterfaces.

    :copyright: (c) 2014 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""
import sys
import time
from uuid import uuid4
try:
    import cPickle as pickle
except ImportError:
    import pickle

from flask.sessions import SessionInterface, SessionMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature
from werkzeug.datastructures import CallbackDict


class ServerSideSession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""

    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.permanent = True
        self.modified = False


class RedisSession(ServerSideSession):
    pass


class MemcachedSession(ServerSideSession):
    pass


class FileSystemSession(ServerSideSession):
    pass


class MongoDBSession(ServerSideSession):
    pass


class BaseSessionInterface(SessionInterface):

    def __init__(self, client, key_prefix):
        self.client = self._get_client(client)
        self.key_prefix = key_prefix

    def _get_client(client):
        raise NotImplemented()

    def get_value(self, key):
        return self.client.get(key)

    def set_value(self, key, value, timeout):
        return self.client.set(key, value, timeout)

    def delete_value(self, key):
        return self.client.delete(key)

    def _generate_sid(self, app):
        return self._signer(app).dumps(str(uuid4()))

    def _signer(self, app):
        if not hasattr(self, '_signer_serializer'):
            self._signer_serializer = URLSafeTimedSerializer(app.secret_key)
        return self._signer_serializer

    def _encode_key(self, key, encoding='utf-8'):
        if sys.version_info.major == 2:
            if isinstance(key, unicode):
                return key.encode(encoding)
        else:
            if isinstance(key, bytes):
                return key.decode(encoding)
        return key

    def _session_key(self, app, raw_sid):
        max_age = app.permanent_session_lifetime.total_seconds()
        sid = self._signer(app).loads(raw_sid, max_age=max_age)
        return self._encode_key('{}:{}'.format(self.key_prefix, sid))

    def _session_timeout(self, app):
        return int(app.permanent_session_lifetime.total_seconds())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self._generate_sid(app)
            return self.session_class(sid=sid)
        try:
            val = self.get_value(self._session_key(app, sid))
        except BadSignature:
            val = None
        if val is not None:
            try:
                data = self.serializer.loads(val)
                return self.session_class(data, sid=sid)
            except:
                pass
        return self.session_class(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        try:
            full_session_key = self._session_key(app, session.sid)
        except BadSignature:
            response.delete_cookie(app.session_cookie_name,
                                   domain=domain, path=path)
            return

        if not session:
            if session.modified:
                self.delete_value(full_session_key)
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        # Modification case.  There are upsides and downsides to
        # emitting a set-cookie header each request.  The behavior
        # is controlled by the :meth:`should_set_cookie` method
        # which performs a quick check to figure out if the cookie
        # should be set or not.  This is controlled by the
        # SESSION_REFRESH_EACH_REQUEST config flag as well as
        # the permanent flag on the session itself.
        #if not self.should_set_cookie(app, session):
        #    return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.set_value(full_session_key, val, self._session_timeout(app))
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=expires, httponly=httponly,
                            domain=domain, path=path, secure=secure)


class NullSessionInterface(SessionInterface):
    """Used to open a :class:`flask.sessions.NullSession` instance.
    """

    def open_session(self, app, request):
        return None


class RedisSessionInterface(BaseSessionInterface):
    """Uses the Redis key-value store as a session backend.

    :param redis: A ``redis.Redis`` instance.
    :param key_prefix: A prefix that is added to all Redis store keys.
    """

    serializer = pickle
    session_class = RedisSession

    def _get_client(self, client):
        if client is None:
            from redis import Redis
            client = Redis()
        return client

    def set_value(self, key, value, timeout):
        return self.client.setex(key, value, timeout)


class MemcachedSessionInterface(BaseSessionInterface):
    """A Session interface that uses memcached as backend.

    :param client: A ``memcache.Client`` instance.
    :param key_prefix: A prefix that is added to all Memcached store keys.
    """

    serializer = pickle
    session_class = MemcachedSession

    def _get_client(self, client):
        if client is not None:
            return client

        servers = ['127.0.0.1:11211']
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

    def _session_timeout(self, app):
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        timeout = super(MemcachedSessionInterface, self)._session_timeout(app)
        if timeout > 2592000:  # 60*60*24*30, 30 days
            # See http://code.google.com/p/memcached/wiki/FAQ
            # "You can set expire times up to 30 days in the future. After that
            # memcached interprets it as a date, and will expire the item after
            # said date. This is a simple (but obscure) mechanic."
            #
            # This means that we have to switch to absolute timestamps.
            timeout += int(time.time())
        return timeout


class FileSystemSessionInterface(BaseSessionInterface):
    """Uses the :class:`werkzeug.contrib.cache.FileSystemCache` as a session
    backend.

    :param cache_dir: the directory where session files are stored.
    :param threshold: the maximum number of items the session stores before it
                      starts deleting some.
    :param mode: the file mode wanted for the session files, default 0600
    :param key_prefix: A prefix that is added to FileSystemCache store keys.
    """

    session_class = FileSystemSession
    serializer = pickle

    def __init__(self, cache_dir, threshold, mode, key_prefix):
        self._cache_dir = cache_dir
        self._threshold = threshold
        self._mode = mode
        super(FileSystemSessionInterface, self).__init__(None, key_prefix)

    def _get_client(self, client):
        from werkzeug.contrib.cache import FileSystemCache
        return FileSystemCache(self._cache_dir, threshold=self._threshold, mode=self._mode)


class MongoDBSessionInterface(BaseSessionInterface):
    """A Session interface that uses mongodb as backend.

    :param client: A ``pymongo.MongoClient`` instance.
    :param db: The database you want to use.
    :param collection: The collection you want to use.
    :param key_prefix: A prefix that is added to all MongoDB store keys.
    """

    serializer = pickle
    session_class = MongoDBSession

    def __init__(self, client, db, collection, key_prefix):
        self._db = db
        self._collection = collection
        super(MongoDBSessionInterface, self).__init__(client, key_prefix)

    def _get_client(self, client):
        if client is None:
            from pymongo import MongoClient
            client = MongoClient()
        return client[self._db][self._collection]

    def get_value(self, key):
        document = self.client.find_one({'id': key})
        if not document:
            return None
        return str(document['val'])

    def set_value(self, key, value, timeout):
        return self.client.update({'id': key},
                                  {'id': key,
                                   'val': value}, True)

    def delete_value(self, key):
        super(MongoDBSessionInterface, self).delete_value({'id': key})
