import json
from contextlib import contextmanager

import flask
from redis import Redis

from flask_session import __version__
from flask_session.redis import RedisSession


class TestRedisSession:
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

    def retrieve_stored_session(self, key):
        return self.r.get(key)

    def test_redis_default(self, app_utils):
        with self.setup_redis():
            app = app_utils.create_app(
                {"SESSION_TYPE": "redis", "SESSION_REDIS": self.r}
            )

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

    def test_redis_adds_version_info(self, app_utils):
        """Test that RedisSessionInterface adds Flask-Session version info when creating default client."""
        with self.setup_redis():
            # Don't provide a Redis client, let it create one with version info
            app = app_utils.create_app({"SESSION_TYPE": "redis"})

            with app.test_request_context():
                # Access the session interface to trigger client creation
                session_interface = app.session_interface

                # Check that lib_name was set in connection pool;
                # lib_version is left to redis-py's own default
                conn_kwargs = session_interface.client.connection_pool.connection_kwargs
                expected_lib_name = f"redis-py(flask-session_v{__version__})"
                assert conn_kwargs.get("lib_name") == expected_lib_name

    def test_redis_respects_custom_version_info(self, app_utils):
        """Test that custom lib_name and lib_version are not overridden."""
        with self.setup_redis():
            # Create a Redis client with custom version info
            custom_client = Redis(lib_name="MyCustomApp", lib_version="1.2.3")

            app = app_utils.create_app(
                {"SESSION_TYPE": "redis", "SESSION_REDIS": custom_client}
            )

            with app.test_request_context():
                session_interface = app.session_interface

                # Check that custom values were preserved
                conn_kwargs = session_interface.client.connection_pool.connection_kwargs
                assert conn_kwargs.get("lib_name") == "MyCustomApp"
                assert conn_kwargs.get("lib_version") == "1.2.3"
