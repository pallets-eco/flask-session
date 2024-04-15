import json
from contextlib import contextmanager
from datetime import timedelta

import flask
from flask_session.redis import RedisSession
from itsdangerous import want_bytes
from redis import Redis
from tests.utils import session_permanent, session_refresh_each_request

from tests.abs_test import ABSTestSession


class TestRedisSession(ABSTestSession):
    """This requires package: redis"""

    @contextmanager
    def setup_redis(self):
        self.r = Redis()
        try:
            self.r.flushall()
            yield
        finally:
            self.r.flushall()
            self.r.close()

    def retrieve_stored_session(self, key, app):
        doc = self.r.get(key)
        return json.loads(want_bytes(doc).decode("utf-8")) if want_bytes(doc) else {}

    @session_permanent
    @session_refresh_each_request
    def test_default(self, app_utils, _session_permanent,
                     _session_refresh_each_request):
        with self.setup_redis():
            app = app_utils.create_app(
                {"SESSION_TYPE": "redis",
                 "SESSION_REDIS": self.r,
                 "SESSION_PERMANENT": _session_permanent,
                 "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                 }
            )

            with app.test_request_context():
                assert isinstance(flask.session, RedisSession)
                self._default_test(app_utils, app)

    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                      _session_permanent,
                      _session_refresh_each_request):
        with self.setup_redis():
            app = app_utils.create_app(
                {"SESSION_TYPE": "redis",
                 "SESSION_REDIS": self.r,
                 "SESSION_PERMANENT": _session_permanent,
                 "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                 "PERMANENT_SESSION_LIFETIME": timedelta(seconds=5),

                 }
            )

            with app.test_request_context():
                self._test_lifetime(app, _session_permanent)
