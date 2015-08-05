import unittest
import tempfile

import flask
from flask.ext.session import Session


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
        app = flask.Flask(__name__)
        app.config['SESSION_TYPE'] = 'redis'
        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']
        @app.route('/delete', methods=['POST'])
        def delete():
            del flask.session['value']
            return 'value deleted'

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')
        c.post('/delete')
    
    
    def test_memcached_session(self):
        app = flask.Flask(__name__)
        app.config['SESSION_TYPE'] = 'memcached'
        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']
        @app.route('/delete', methods=['POST'])
        def delete():
            del flask.session['value']
            return 'value deleted'

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')
        c.post('/delete')
    
    
    def test_filesystem_session(self):
        app = flask.Flask(__name__)
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']
        @app.route('/delete', methods=['POST'])
        def delete():
            del flask.session['value']
            return 'value deleted'

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')
        c.post('/delete')
    
    def test_mongodb_session(self):
        app = flask.Flask(__name__)
        app.config['SESSION_TYPE'] = 'mongodb'
        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']
        @app.route('/delete', methods=['POST'])
        def delete():
            del flask.session['value']
            return 'value deleted'

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')
        c.post('/delete')

    def test_flasksqlalchemy_session(self):
        app = flask.Flask(__name__)
        app.debug = True
        app.config['SESSION_TYPE'] = 'sqlalchemy'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']
        @app.route('/delete', methods=['POST'])
        def delete():
            del flask.session['value']
            return 'value deleted'

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value '
                                                                    b'set')
        self.assertEqual(c.get('/get').data, b'42')
        c.post('/delete')

    def test_session_use_signer(self):
        app = flask.Flask(__name__)
        app.secret_key = 'test_secret_key'
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_USE_SIGNER'] = True
        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')

        # Verify UUID and (160 bit HMAC now encoded in base64) as cookie value
        #   e.g. '91639adf-34e0-4ddf-bae2-ebf0be6315ac.6V94YwDyIMe4G6uqUzYrDAhLevg'
        # https://github.com/mitsuhiko/itsdangerous/blob/0.24/itsdangerous.py#L201-L207
        session_cookie = [cookie for cookie in c.cookie_jar if cookie.name == 'session'][0]
        self.assertRegexpMatches(session_cookie.value, r'^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}\.[a-zA-Z0-9\-_]{27}$')

    def test_session_use_custom_signer(self):
        app = flask.Flask(__name__)
        app.secret_key = 'test_secret_key'
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_SIGNER_TYPE'] = 'hmac_sha256'
        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')

        # Verify UUID and (256 bit HMAC now encoded in base64) as cookie value
        #   e.g. '91639adf-34e0-4ddf-bae2-ebf0be6315ac.6V94YwDyIMe4G6uqUzYrDAhLevg'
        # https://github.com/mitsuhiko/itsdangerous/blob/0.24/itsdangerous.py#L201-L207
        session_cookie = [cookie for cookie in c.cookie_jar if cookie.name == 'session'][0]
        self.assertRegexpMatches(session_cookie.value, r'^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}\.[a-zA-Z0-9\-_]{43}$')

if __name__ == "__main__":
    unittest.main()
