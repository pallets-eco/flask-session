import unittest
import tempfile

import flask
from flask.ext.session import Session


class FlaskSessionTestCase(unittest.TestCase):
    def _get_cookie_dict(self, test_client):
        return {
            cookie.name: cookie
            for cookie in test_client.cookie_jar
        }

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
            return flask.session.get('value', '')
        @app.route('/delete', methods=['POST'])
        def delete():
            del flask.session['value']
            return 'value deleted'
        @app.route('/destroy', methods=['POST'])
        def destroy():
            app.session_interface.destroy(flask.session)
            return 'session destroyed'
        @app.route('/regenerate', methods=['POST'])
        def regenerate():
            app.session_interface.regenerate(flask.session)
            return 'session regenerated'
        @app.errorhandler(500)
        def errorhandler_500(exc):
            raise exc

        # Create, retrieve, delete tests
        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')
        c.post('/delete')
        self.assertEqual(c.get('/get').data, b'')

        # Destruction test
        # Verify destruction works
        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        session_cookie = self._get_cookie_dict(c)['session']
        c.post('/destroy')
        self.assertNotIn('session', self._get_cookie_dict(c))

        # Verify our session was erased from the underlying store
        # `session=abcdef-original-session-id`
        cookie_header = 'session={value}'.format(value=session_cookie.value)
        self.assertEqual(app.test_client().get('/get', headers={'Cookie': cookie_header}).data, b'')

        # Regeneration test
        # Verify regeneration preserves data but gives us a new session id
        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        original_session_cookie = self._get_cookie_dict(c)['session']
        c.post('/regenerate')
        self.assertEqual(c.get('/get').data, b'42')
        self.assertNotEqual(self._get_cookie_dict(c)['session'].value, original_session_cookie.value)

        # Verify our original session was erased from the underlying store
        # `session=abcdef-original-session-id`
        cookie_header = 'session={value}'.format(value=original_session_cookie.value)
        self.assertEqual(app.test_client().get('/get', headers={'Cookie': cookie_header}).data, b'')

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

if __name__ == "__main__":
    unittest.main()
