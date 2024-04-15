import json
from contextlib import contextmanager

import flask
import pytest

from flask_session.mongodb import MongoDBSession
from itsdangerous import want_bytes
from pymongo import MongoClient
from datetime import timedelta
from tests.utils import session_permanent, session_refresh_each_request

from tests.abs_test import ABSTestSession


class TestMongoSession(ABSTestSession):
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

    def retrieve_stored_session(self, key, app):
        document = self.collection.find_one({"id": key})
        return json.loads(want_bytes(document["val"]).decode("utf-8")) if want_bytes(document["val"]) else {}

    @session_permanent
    @session_refresh_each_request
    def test_default(self, app_utils, _session_permanent,
                     _session_refresh_each_request):
        with self.setup_mongo():
            app = app_utils.create_app(
                {
                    "SESSION_TYPE": "mongodb",
                    "SESSION_MONGODB": self.client,
                    "SESSION_PERMANENT": _session_permanent,
                    "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,

                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, MongoDBSession)
                self._default_test(app_utils, app)

    # TODO: fix this test (issue with TTL index)
    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                                 _session_permanent,
                                 _session_refresh_each_request):
        pytest.skip("TTL index issue")
    #     with self.setup_mongo():
    #
    #         app = app_utils.create_app(
    #             {
    #                 "SESSION_TYPE": "mongodb",
    #                 "SESSION_MONGODB": self.client,
    #                 "SESSION_PERMANENT": _session_permanent,
    #                 "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
    #                 "PERMANENT_SESSION_LIFETIME": timedelta(seconds=5),
    #             }
    #         )
    #
    #         with app.test_request_context():
    #             assert isinstance(flask.session, MongoDBSession)
    #             self._test_lifetime(app, _session_permanent)
