import unittest
import tempfile

import flask
from flask.ext.session import Session
from time import sleep


class FlaskSessionTestCase(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['SECRET_KEY'] = 'foo'
        app.debug = True

        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'

        @app.route('/get')
        def get():
            return flask.session.get('value', 'Nothing set')

        self.app = app

    def init_client(self, config):
        self.app.config.update(config)
        Session(self.app)
        self.client = self.app.test_client()

    def _test_backend(self, kind, config=None):
        if config is None:
            config = {}
        config['SESSION_TYPE'] = kind
        self.init_client(config)
        self.assertEqual(self.client.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(self.client.get('/get').data, b'42')

    def test_null_session(self):
        self.init_client({})

        def expect_exception(f, *args, **kwargs):
            try:
                f(*args, **kwargs)
            except RuntimeError as e:
                self.assertTrue(e.args and 'session is unavailable' in e.args[0])
            else:
                self.assertTrue(False, 'expected exception')

        with self.app.test_request_context():
            self.assertTrue(flask.session.get('missing_key') is None)
            expect_exception(flask.session.__setitem__, 'foo', 42)
            expect_exception(flask.session.pop, 'foo')

    def test_redis_session(self):
        self._test_backend('redis')

    def test_memcached_session(self):
        self._test_backend('redis')

    def test_filesystem_session(self):
        self._test_backend('filesystem', {'SESSION_FILE_DIR': tempfile.gettempdir()})

    def test_mongodb_session(self):
        self._test_backend('mongodb')

    def test_expired_session(self):
        self.init_client({'SESSION_TYPE': 'filesystem',
                          'SESSION_FILE_DIR': tempfile.gettempdir(),
                          'PERMANENT_SESSION_LIFETIME': 0.001})
        self.assertEqual(self.client.post('/set', data={'value': '42'}).data, b'value set')
        sleep(0.002)
        self.assertEqual(self.client.get('/get').data, 'Nothing set')


if __name__ == '__main__':
    unittest.main()
