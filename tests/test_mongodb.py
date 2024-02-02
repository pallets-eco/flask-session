import flask
import flask_session


class TestMongoDB:
    def test_basic(self, app_utils):
        app = app_utils.create_app({"SESSION_TYPE": "mongodb"})

        # Should be using MongoDB
        with app.test_request_context():
            isinstance(flask.session, flask_session.sessions.MongoDBSession)

        # TODO: Need to test with mongodb service running, once
        # that is available, then we can call
        # app_utils.test_session_set
