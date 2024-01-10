import flask
import flask_session


class TestMemcached:
    """This requires package: memcached
    This needs to be running before test runs
    """

    def test_basic(self, app_utils):
        app = app_utils.create_app({"SESSION_TYPE": "memcached"})

        # Should be using Memecached
        with app.test_request_context():
            isinstance(flask.session, flask_session.sessions.MemcachedSessionInterface)

        app_utils.test_session_set(app)
