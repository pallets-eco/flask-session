import os
import shutil
from contextlib import contextmanager
from datetime import timedelta

import flask
from tests.utils import session_permanent, session_refresh_each_request
from cachelib.file import FileSystemCache
from flask_session.cachelib import CacheLibSession
from tests.abs_test import ABSTestSession


class TestCachelibSession(ABSTestSession):
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
    def test_default(self, app_utils,_session_permanent,
                                     _session_refresh_each_request):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "cachelib",
                "SESSION_SERIALIZATION_FORMAT": "json",
                "SESSION_PERMANENT": _session_permanent,
                "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                "SESSION_CACHELIB": FileSystemCache(
                    threshold=500, cache_dir=self.session_dir
                ),
            }
        )

        # Should be using CacheLib (FileSystem)
        with self.setup_filesystem(), app.test_request_context():
            assert isinstance(
                flask.session,
                CacheLibSession,
            )
            self._default_test(app_utils, app)

    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                                 _session_permanent,
                                 _session_refresh_each_request):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "cachelib",
                "SESSION_SERIALIZATION_FORMAT": "json",
                "SESSION_PERMANENT": _session_permanent,
                "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                "SESSION_CACHELIB": FileSystemCache(
                    threshold=500, cache_dir=self.session_dir
                ),
                "PERMANENT_SESSION_LIFETIME": timedelta(seconds=4),
            }
        )

        # Should be using FileSystem
        with self.setup_filesystem(), app.test_request_context():
            assert isinstance(
                flask.session,
                CacheLibSession,
            )
            self._test_lifetime(app, _session_permanent)
