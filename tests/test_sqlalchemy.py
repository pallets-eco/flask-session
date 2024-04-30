import json
from contextlib import contextmanager

import flask
import pytest
from flask_session.sqlalchemy import SqlAlchemySession
from sqlalchemy import text


class TestSQLAlchemy:
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
            return session_model.data
        return None

    @pytest.mark.filterwarnings("ignore:No valid SQLAlchemy instance provided")
    def test_use_signer(self, app_utils):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "sqlalchemy",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///",
            }
        )
        with app.app_context() and self.setup_sqlalchemy(
            app
        ) and app.test_request_context():
            assert isinstance(
                flask.session,
                SqlAlchemySession,
            )
            app_utils.test_session(app)

            # Check if the session is stored in SQLAlchemy
            cookie = app_utils.test_session_with_cookie(app)
            session_id = cookie.split(";")[0].split("=")[1]
            byte_string = self.retrieve_stored_session(f"session:{session_id}", app)
            stored_session = (
                json.loads(byte_string.decode("utf-8")) if byte_string else {}
            )
            assert stored_session.get("value") == "44"

    @pytest.mark.filterwarnings("ignore:No valid SQLAlchemy instance provided")
    def test_database_not_created_automatically(self, app_utils):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "sqlalchemy",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///",
                "SESSION_SQLALCHEMY_TABLE_EXISTS": True,
            }
        )
        with app.app_context() and self.setup_sqlalchemy(
            app
        ) and app.test_request_context():
            assert isinstance(
                flask.session,
                SqlAlchemySession,
            )
            with pytest.raises(AssertionError):
                app_utils.test_session(app)
