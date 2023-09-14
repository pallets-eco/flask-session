import unittest
import tempfile

import flask
from flask_session import Session

REDIS_VERSIONS = [6, 7]


class FlaskSessionTestCase(unittest.TestCase):

    def test_null_session(self):
        app = flask.Flask(__name__)
        Session(app)

        def expect_exception(f, *args, **kwargs):
            try:
                f(*args, **kwargs)
            except RuntimeError as e:
                self.assertTrue(e.args and 'session is unavailable' in e.args[0])
            else:
                self.assertTrue(False, 'expected exception')
        with app.test_request_context():
            self.assertTrue(flask.session.get('missing_key') is None)
            expect_exception(flask.session.__setitem__, 'foo', 42)
            expect_exception(flask.session.pop, 'foo')

    def test_redis_session(self):
        import fakeredis
        for r_version in REDIS_VERSIONS:
            app = flask.Flask(__name__)
            app.config['SESSION_TYPE'] = 'redis'
            app.config['SESSION_REDIS'] = fakeredis.FakeStrictRedis(version=r_version)
            app.debug = True
            self._flask_session_assert(app)

    def test_memcached_session(self):
        app = flask.Flask(__name__)
        app.config['SESSION_TYPE'] = 'memcached'
        self._flask_session_assert(app)

    def test_filesystem_session(self):
        app = flask.Flask(__name__)
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
        self._flask_session_assert(app)

    def test_mongodb_session(self):
        app = flask.Flask(__name__)
        app.testing = True
        app.config['SESSION_TYPE'] = 'mongodb'
        self._flask_session_assert(app)

    def test_flasksqlalchemy_session(self):
        app = flask.Flask(__name__)
        app.debug = True
        app.config['SESSION_TYPE'] = 'sqlalchemy'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        self._flask_session_assert(app)

    def test_flasksqlalchemy_session_with_signer(self):
        app = flask.Flask(__name__)
        app.debug = True
        app.secret_key = 'test_secret_key'
        app.config['SESSION_TYPE'] = 'sqlalchemy'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        app.config['SESSION_USE_SIGNER'] = True

        self._flask_session_assert(app)

    def test_session_use_signer(self):
        import fakeredis
        for r_version in REDIS_VERSIONS:
            app = flask.Flask(__name__)
            app.secret_key = 'test_secret_key'
            app.config['SESSION_TYPE'] = 'redis'
            app.config['SESSION_REDIS'] = fakeredis.FakeStrictRedis(version=r_version)
            app.config['SESSION_USE_SIGNER'] = True
            self._flask_session_assert(app)

    def _flask_session_assert(self, app: flask.Flask):
        Session(app)

        @app.route('/set', methods=['POST'])
        def _set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'

        @app.route('/get')
        def _get():
            return flask.session['value']

        @app.route('/delete', methods=['POST'])
        def _delete():
            del flask.session['value']
            return 'value deleted'

        with app.test_client() as c:
            self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
            self.assertEqual(c.get('/get').data, b'42')
            c.post('/delete')


if __name__ == "__main__":
    unittest.main()
