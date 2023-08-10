import flask
from redis import Redis
import flask_session
import pytest

class TestRedisSession:

    def setup_method(self, method):
        # Clear redis
        r = Redis()
        r.flushall()

    def _has_redis_prefix(self, prefix):
        r = Redis()
        for key in r.keys():
            if key.startswith(prefix):
                return True
        return False

    def test_redis_default(self, app_utils):
        app = app_utils.create_app({
            'SESSION_TYPE': 'redis'
        })

        # Should be using Redis class
        with app.test_request_context():
            isinstance(flask.session, flask_session.sessions.RedisSession)

        app_utils.test_session_set(app)

        # There should be a session:<UUID> object
        assert self._has_redis_prefix(b'session:')

    def test_redis_key_prefix(self, app_utils):
        app = app_utils.create_app({
            'SESSION_TYPE': 'redis',
            'SESSION_KEY_PREFIX': 'sess-prefix:'
        })
        app_utils.test_session_set(app)

        # There should be a key in Redis that starts with the prefix set
        assert not self._has_redis_prefix(b'session:')
        assert self._has_redis_prefix(b'sess-prefix:')

    def test_redis_with_signer(self, app_utils):
        app = app_utils.create_app({
            'SESSION_TYPE': 'redis',
            'SESSION_USE_SIGNER': True,
        })
        # Without a secret key set, there should be an exception raised
        with pytest.raises(AssertionError):
            app_utils.test_session_set(app)

        # With a secret key set, no exception should be thrown
        app.secret_key = 'test_key'
        app_utils.test_session_set(app)

        # There should be a key in Redis that starts with the prefix set
        assert self._has_redis_prefix(b'session:')
