import sys
import uuid
from datetime import datetime
import pickle

from flask.sessions import SessionInterface as FlaskSessionInterface
from flask.sessions import SessionMixin
from werkzeug.datastructures import CallbackDict
from itsdangerous import want_bytes

from cachelib.file import FileSystemCache


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


class MemcachedSession(ServerSideSession):
    pass


class FileSystemSession(ServerSideSession):
    pass


class MongoDBSession(ServerSideSession):
    pass


class FileSystemSessionInterface(FlaskSessionInterface):
    """
    Uses the :class:`cachelib.file.FileSystemCache` as a session backend.

    :param cache_dir: the directory where session files are stored.
    :param threshold: the maximum number of items the session stores before it
                      starts deleting some.
    :param mode: the file mode wanted for the session files, default 0600
    :param key_prefix: A prefix that is added to FileSystemCache store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    session_class = FileSystemSession
    
    def _generate_sid(self):
        return str(uuid.uuid4())

    def __init__(self, cache_dir, threshold, mode, key_prefix, cookie_name, permanent=True):
        self.cache = FileSystemCache(cache_dir, threshold=threshold, mode=mode)
        self.key_prefix = key_prefix
        self.permanent = permanent
        self.has_same_site_capability = hasattr(self, "get_cookie_samesite")
        self.cookie_name = cookie_name

    def open_session(self, app, request):
        sid = request.cookies.get(self.cookie_name)

        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid, permanent=self.permanent)

        data = self.cache.get(self.key_prefix + sid)
        if data is not None:
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                self.cache.delete(self.key_prefix + session.sid)
                response.delete_cookie(
                    self.cookie_name, domain=domain, path=path
                )
            return

        conditional_cookie_kwargs = {}
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        if self.has_same_site_capability:
            conditional_cookie_kwargs["samesite"] = self.get_cookie_samesite(app)
        expires = self.get_expiration_time(app, session)
        data = dict(session)
        self.cache.set(
            self.key_prefix + session.sid,
            data,
            total_seconds(app.permanent_session_lifetime),
        )

        response.set_cookie(
            self.cookie_name,
            session.sid,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            **conditional_cookie_kwargs
        )


class MongoDBSessionInterface(FlaskSessionInterface):
    """A Session interface that uses mongodb as backend.

    :param client: A ``pymongo.MongoClient`` instance.
    :param db: The database you want to use.
    :param collection: The collection you want to use.
    :param key_prefix: A prefix that is added to all MongoDB store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    serializer = pickle
    session_class = MongoDBSession
    
    def _generate_sid(self):
        return str(uuid.uuid4())

    def __init__(self, client, db, collection, key_prefix, cookie_name, permanent=True):
        self.client = client
        self.store = client[db][collection]
        self.key_prefix = key_prefix
        self.permanent = permanent
        self.has_same_site_capability = hasattr(self, "get_cookie_samesite")
        self.cookie_name = cookie_name

    def open_session(self, app, request):
        # Get the session id from the cookie
        sid = request.cookies.get(self.cookie_name)
        
        print(request.cookies)

        # If the session id does not exist, generate a new one
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid, permanent=self.permanent)

        # Get the session document from the database
        store_id = self.key_prefix + sid
        document = self.store.find_one({"id": store_id})

        # If the session document exists, check if it has expired
        if document:
            # Get the expiration time from the document
            expiration = document.get("expiration")

            # Check if expiration exists and compare it to the current time
            if expiration is not None and expiration <= datetime.utcnow():
                # If the expiration time is less than or equal to the current time (expired), delete the document
                self.store.delete_one({"id": store_id})
                document = None

        # If the session document still exists after checking for expiration, load the session data from the document
        if document:
            try:
                val = document["val"]
                data = self.serializer.loads(want_bytes(val))
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid, permanent=self.permanent)

        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        # Get the domain and path for the cookie from the app
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # Generate a store id from the session id
        store_id = self.key_prefix + session.sid

        # If the session does not exist, delete the session document and cookie
        if not session:
            # Check if the session was modified
            if session.modified:
                # Delete the session document
                self.store.delete_one({"id": store_id})

                # Delete the session cookie
                response.delete_cookie(
                    self.cookie_name, domain=domain, path=path
                )

            return

        # Set the cookie parameters
        conditional_cookie_kwargs = {}

        # Set the httponly and secure parameters if the capability exists
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)

        # Set the samesite parameter if the capability exists
        if self.has_same_site_capability:
            conditional_cookie_kwargs["samesite"] = self.get_cookie_samesite(app)

        # Get the expiration time for the session
        expires = self.get_expiration_time(app, session)

        # Serialize the session data
        val = self.serializer.dumps(dict(session))

        # Update the session document in the database
        self.store.update_one(
            {"id": store_id},
            {"$set": {"id": store_id, "val": val, "expiration": expires}},
            True,
        )
        
        print(self.cookie_name, session.sid, expires, httponly, domain, path, secure, conditional_cookie_kwargs)
        print(type(self.cookie_name), type(session.sid), type(expires), type(httponly), type(domain), type(path), type(secure), type(conditional_cookie_kwargs))

        # Set the cookie
        response.set_cookie(
            key=self.cookie_name,
            value=session.sid,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            **conditional_cookie_kwargs
        )
