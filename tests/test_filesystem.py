import tempfile

import flask
import flask_session


class TestFileSystem:
    def setup_method(self, _):
        pass

    def test_basic(self, app_utils):
        app = app_utils.create_app(
            {"SESSION_TYPE": "filesystem", "SESSION_FILE_DIR": tempfile.gettempdir()}
        )
        app_utils.test_session_set(app)

        # Should be using FileSystem class
        with app.test_request_context():
            isinstance(flask.session, flask_session.sessions.FileSystemSession)
