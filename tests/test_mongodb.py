import json
from contextlib import contextmanager

import flask
from flask_session.mongodb import MongoDBSession
from itsdangerous import want_bytes
from pymongo import MongoClient


class TestMongoSession:
    """This requires package: pymongo"""

    @contextmanager
    def setup_mongo(self):
        self.client = MongoClient()
        self.db = self.client.flask_session
        self.collection = self.db.sessions
        try:
            self.collection.delete_many({})
            yield
        finally:
            self.collection.delete_many({})
            self.client.close()

    def retrieve_stored_session(self, key):
        document = self.collection.find_one({"id": key})
        return want_bytes(document["val"])

    def test_mongo_default(self, app_utils):
        with self.setup_mongo():
            app = app_utils.create_app(
                {
                    "SESSION_TYPE": "mongodb",
                    "SESSION_MONGODB": self.client,
                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, MongoDBSession)
                app_utils.test_session(app)

                # Check if the session is stored in MongoDB
                cookie = app_utils.test_session_with_cookie(app)
                session_id = cookie.split(";")[0].split("=")[1]
                byte_string = self.retrieve_stored_session(f"session:{session_id}")
                stored_session = (
                    json.loads(byte_string.decode("utf-8")) if byte_string else {}
                )
                assert stored_session.get("value") == "44"
