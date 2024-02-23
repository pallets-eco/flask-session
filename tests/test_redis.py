import json
from contextlib import contextmanager

import flask
from flask_session.redis import RedisSession
from redis import Redis


class TestRedisSession:
    """This requires package: redis"""

    @contextmanager
    def setup_redis(self):
        try:
            self.r = Redis()
            self.r.flushall()
            yield
        finally:
            self.r.flushall()
            self.r.close()

    def retrieve_stored_session(self, key):
        return self.r.get(key)

    def test_redis_default(self, app_utils):
        with self.setup_redis():
            app = app_utils.create_app({"SESSION_TYPE": "redis"})

            with app.test_request_context():
                assert isinstance(flask.session, RedisSession)
                app_utils.test_session(app)

                # Check if the session is stored in Redis
                cookie = app_utils.test_session_with_cookie(app)
                session_id = cookie.split(";")[0].split("=")[1]
                byte_string = self.retrieve_stored_session(f"session:{session_id}")
                stored_session = (
                    json.loads(byte_string.decode("utf-8")) if byte_string else {}
                )
                assert stored_session.get("value") == "44"
