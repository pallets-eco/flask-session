import os
import shutil
from contextlib import contextmanager
from datetime import timedelta, datetime, timezone

import time
import flask
from flask_session.filesystem import FileSystemSession
from tests.utils import session_permanent, session_refresh_each_request

from tests.abs_test import ABSTestSession


class TestFileSystemSession(ABSTestSession):
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

    @session_permanent
    @session_refresh_each_request
    def test_default(self, app_utils, _session_permanent,
                                _session_refresh_each_request):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "filesystem",
                "SESSION_FILE_DIR": self.session_dir,
                "SESSION_PERMANENT": _session_permanent,
                "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
            }
        )

        # Should be using FileSystem
        with self.setup_filesystem(), app.test_request_context():
            assert isinstance(
                flask.session,
                FileSystemSession,
            )
            self._default_test(app_utils, app)

    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                                 _session_permanent,
                                 _session_refresh_each_request):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "filesystem",
                "SESSION_FILE_DIR": self.session_dir,
                "SESSION_PERMANENT": _session_permanent,
                "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                "PERMANENT_SESSION_LIFETIME": timedelta(seconds=4),
            }
        )

        # Should be using FileSystem
        with self.setup_filesystem(), app.test_request_context():
            assert isinstance(
                flask.session,
                FileSystemSession,
            )
            self._test_lifetime(app, _session_permanent)
