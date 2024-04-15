import json
from contextlib import contextmanager
from datetime import timedelta

import flask
import pytest
from flask_session.sqlalchemy import SqlAlchemySession
from sqlalchemy import text
from tests.utils import session_permanent, session_refresh_each_request

from tests.abs_test import ABSTestSession


class TestSQLAlchemy(ABSTestSession):
    """This requires package: sqlalchemy"""

    @contextmanager
    def setup_sqlalchemy(self, app):
        try:
            app.session_interface.client.session.execute(text("DELETE FROM sessions"))
            app.session_interface.client.session.commit()
            yield
        finally:
            app.session_interface.client.session.execute(text("DELETE FROM sessions"))
            app.session_interface.client.session.close()

    def retrieve_stored_session(self, key, app):
        session_model = (
            app.session_interface.client.session.query(
                app.session_interface.sql_session_model
            )
            .filter_by(session_id=key)
            .first()
        )
        if session_model:
            return json.loads(session_model.data.decode("utf-8")) if session_model.data else {}
        return {}

    @session_permanent
    @session_refresh_each_request
    @pytest.mark.filterwarnings("ignore:No valid SQLAlchemy instance provided")
    def test_default(self, app_utils, _session_permanent,
                     _session_refresh_each_request):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "sqlalchemy",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///",
                "SESSION_PERMANENT": _session_permanent,
                "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
            }
        )
        with app.app_context() and self.setup_sqlalchemy(
            app
        ) and app.test_request_context():
            assert isinstance(
                flask.session,
                SqlAlchemySession,
            )
            self._default_test(app_utils, app)

    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                      _session_permanent,
                      _session_refresh_each_request):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "sqlalchemy",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///",
                "SESSION_PERMANENT": _session_permanent,
                "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                "PERMANENT_SESSION_LIFETIME": timedelta(seconds=5),

            }
        )
        with app.app_context() and self.setup_sqlalchemy(
            app
        ) and app.test_request_context():
            assert isinstance(
                flask.session,
                SqlAlchemySession,
            )
            self._test_lifetime(app, _session_permanent)
