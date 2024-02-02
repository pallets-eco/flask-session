import flask
import flask_session


class TestSQLAlchemy:
    def test_basic(self, app_utils):
        app = app_utils.create_app(
            {"SESSION_TYPE": "sqlalchemy", "SQLALCHEMY_DATABASE_URI": "sqlite:///"}
        )

        # Should be using SqlAlchemy
        with app.test_request_context():
            isinstance(flask.session, flask_session.sessions.SqlAlchemySession)
            app.session_interface.db.create_all()

        app_utils.test_session_set(app)
        app_utils.test_session_modify(app)

    def test_use_signer(self, app_utils):
        app = app_utils.create_app(
            {
                "SESSION_TYPE": "sqlalchemy",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///",
                "SQLALCHEMY_USE_SIGNER": True,
            }
        )

        with app.test_request_context():
            app.session_interface.db.create_all()

        app_utils.test_session_set(app)
