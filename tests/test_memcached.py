import json
from contextlib import contextmanager

import flask
import memcache  # Import the memcache library
from flask_session.memcached import MemcachedSession


class TestMemcachedSession:
    """This requires package: python-memcached"""

    @contextmanager
    def setup_memcached(self):
        try:
            self.mc = memcache.Client(["127.0.0.1:11211"], debug=0)
            self.mc.flush_all()
            yield
        finally:
            self.mc.flush_all()
            # Memcached connections are pooled, no close needed

    def retrieve_stored_session(self, key):
        return self.mc.get(key)

    def test_memcached_default(self, app_utils):
        with self.setup_memcached():
            app = app_utils.create_app({"SESSION_TYPE": "memcached"})

            with app.test_request_context():
                assert isinstance(
                    flask.session,
                    MemcachedSession,
                )
                app_utils.test_session(app)

                # Check if the session is stored in Memcached
                cookie = app_utils.test_session_with_cookie(app)
                session_id = cookie.split(";")[0].split("=")[1]
                byte_string = self.retrieve_stored_session(f"session:{session_id}")
                stored_session = (
                    json.loads(byte_string.decode("utf-8")) if byte_string else {}
                )
                assert stored_session.get("value") == "44"
