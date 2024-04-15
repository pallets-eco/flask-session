import json
from contextlib import contextmanager

import flask
import pymemcache as memcache  # Import the memcache library
from flask_session.memcached import MemcachedSession
from tests.utils import session_permanent, session_refresh_each_request

from tests.abs_test import ABSTestSession


class TestMemcachedSession(ABSTestSession):
    """This requires package: python-memcached"""

    @contextmanager
    def setup_memcached(self):
        self.mc = memcache.Client(("127.0.0.1:11211"))
        try:
            self.mc.flush_all()
            yield
        finally:
            self.mc.flush_all()
            # Memcached connections are pooled, no close needed

    def retrieve_stored_session(self, key, app):
        byte_string = self.mc.get(key)
        return json.loads(byte_string.decode("utf-8")) if byte_string else {}

    @session_permanent
    @session_refresh_each_request
    def test_default(self, app_utils, _session_permanent,
                     _session_refresh_each_request):
        with self.setup_memcached():
            app = app_utils.create_app(
                {"SESSION_TYPE": "memcached",
                 "SESSION_MEMCACHED": self.mc,
                 "SESSION_PERMANENT": _session_permanent,
                 "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                 }
            )

            with app.test_request_context():
                assert isinstance(
                    flask.session,
                    MemcachedSession,
                )
                self._default_test(app_utils, app)

    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                                 _session_permanent,
                                 _session_refresh_each_request):
        with self.setup_memcached():
            from datetime import timedelta
            app = app_utils.create_app(
                {"SESSION_TYPE": "memcached",
                 "SESSION_MEMCACHED": self.mc,
                 "SESSION_PERMANENT": _session_permanent,
                 "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                 "PERMANENT_SESSION_LIFETIME": timedelta(seconds=5),
                 }
            )

            with app.test_request_context():
                assert isinstance(
                    flask.session,
                    MemcachedSession,
                )
            self._test_lifetime(app, _session_permanent)
