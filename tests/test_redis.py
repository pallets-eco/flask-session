import flask
import flask_session
from redis import Redis


class TestRedisSession:
    def setup_method(self, method):
        # Clear redis
        r = Redis()
        r.flushall()

    def _has_redis_prefix(self, prefix):
        r = Redis()
        return any(key.startswith(prefix) for key in r.keys()) #noqa SIM118

    def test_redis_default(self, app_utils):
        app = app_utils.create_app({"SESSION_TYPE": "redis"})

        # Should be using Redis
        with app.test_request_context():
            isinstance(flask.session, flask_session.sessions.RedisSession)

        app_utils.test_session_set(app)

        # There should be a session:<UUID> object
        assert self._has_redis_prefix(b"session:")

        self.setup_method(None)
        app_utils.test_session_delete(app)

        # There should not be a session:<UUID> object
        assert not self._has_redis_prefix(b"session:")

    def test_redis_key_prefix(self, app_utils):
        app = app_utils.create_app(
            {"SESSION_TYPE": "redis", "SESSION_KEY_PREFIX": "sess-prefix:"}
        )
        app_utils.test_session_set(app)

        # There should be a key in Redis that starts with the prefix set
        assert not self._has_redis_prefix(b"session:")
        assert self._has_redis_prefix(b"sess-prefix:")

    def test_redis_with_signer(self, app_utils):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "redis",
                "SESSION_USE_SIGNER": True,
            }
        )

        # Without a secret key set, there should be an exception raised
        # TODO: not working
        # with pytest.raises(KeyError):
        #     app_utils.test_session_set(app)

        # With a secret key set, no exception should be thrown
        app.secret_key = "test_key"
        app_utils.test_session_set(app)

        # There should be a key in Redis that starts with the prefix set
        assert self._has_redis_prefix(b"session:")

        # Clear redis
        self.setup_method(None)

        # Check that the session is signed
        app_utils.test_session_sign(app)
