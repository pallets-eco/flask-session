import os
import shutil
from contextlib import contextmanager

import flask
from flask_session.filesystem import FileSystemSession


class TestFileSystemSession:
    session_dir = "testing_session_storage"

    @contextmanager
    def setup_filesystem(self):
        try:
            yield
        finally:
            pass
            if self.session_dir and os.path.isdir(self.session_dir):
                shutil.rmtree(self.session_dir)

    def retrieve_stored_session(self, key, app):
        return app.session_interface.cache.get(key)

    def test_filesystem_default(self, app_utils):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "filesystem",
                "SESSION_FILE_DIR": self.session_dir,
            }
        )

        # Should be using FileSystem
        with self.setup_filesystem(), app.test_request_context():
            assert isinstance(
                flask.session,
                FileSystemSession,
            )
            app_utils.test_session(app)

            # Check if the session is stored in the filesystem
            cookie = app_utils.test_session_with_cookie(app)
            session_id = cookie.split(";")[0].split("=")[1]
            stored_session = self.retrieve_stored_session(f"session:{session_id}", app)
            assert stored_session.get("value") == "44"
