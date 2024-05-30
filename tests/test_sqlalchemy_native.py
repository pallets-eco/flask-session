import json
from contextlib import contextmanager

import flask
from flask_session.sqlalchemy_native import NativeSqlAlchemySession
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session


class TestNativeSQLAlchemy:
    """This requires package: sqlalchemy"""

    @contextmanager
    def setup_sqlalchemy(self, app):
        try:
            with Session(app.session_interface.engine) as session:
                session.execute(text("DELETE FROM sessions"))
                session.commit()
            yield
        finally:
            with Session(app.session_interface.engine) as session:
                session.execute(text("DELETE FROM sessions"))
                session.close()

    def retrieve_stored_session(self, key, app):
        with Session(app.session_interface.engine) as session:
            session_model = session.scalars(
                select(app.session_interface.sql_session_model)
                .where(app.session_interface.sql_session_model.session_id == key)
            ).first()
        if session_model:
            return session_model.data
        return None

    def test_use_signer(self, app_utils):
        engine = create_engine("sqlite:///")
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "sqlalchemy_native",
                "SESSION_SQLALCHEMY_ENGINE": engine,
            }
        )
        with app.app_context() and self.setup_sqlalchemy(
            app
        ) and app.test_request_context():
            assert isinstance(
                flask.session,
                NativeSqlAlchemySession,
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
