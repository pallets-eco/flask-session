from contextlib import contextmanager
from datetime import timedelta

import boto3
import flask
from flask_session.defaults import Defaults
from flask_session.dynamodb import DynamoDBSession
from tests.utils import session_permanent, session_refresh_each_request

from tests.abs_test import ABSTestSession


class TestDynamoDBSession(ABSTestSession):
    """This requires package: boto3"""

    @contextmanager
    def setup_dynamodb(self):
        self.client = boto3.resource(
            "dynamodb",
            endpoint_url="http://localhost:8000",
            region_name="us-west-2",
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        )
        try:
            self.store = self.client.Table(Defaults.SESSION_DYNAMODB_TABLE)
            scan = self.store.scan()
            with self.store.batch_writer() as batch:
                for each in scan.get("Items"):
                    batch.delete_item(
                        Key={
                            "id": each.get("id"),
                        }
                    )
        except self.client.meta.client.exceptions.ResourceNotFoundException:
            pass
        yield
        scan = self.store.scan()
        with self.store.batch_writer() as batch:
            for each in scan.get("Items"):
                batch.delete_item(
                    Key={
                        "id": each.get("id"),
                    }
                )

    def test_dynamodb_default(self, app_utils):
        with self.setup_dynamodb():
            app = app_utils.create_app(
                {
                    "SESSION_TYPE": "dynamodb",
                    "SESSION_DYNAMODB": self.client,
                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, DynamoDBSession)
                app_utils.test_session(app)


    @session_permanent
    @session_refresh_each_request
    def test_default(self, app_utils, _session_permanent,
                     _session_refresh_each_request):
        with self.setup_dynamodb():
            app = app_utils.create_app(
                {
                    "SESSION_TYPE": "dynamodb",
                    "SESSION_DYNAMODB": self.client,
                    "SESSION_PERMANENT": _session_permanent,
                    "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,

                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, DynamoDBSession)
                self._default_test(app_utils, app)

    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                      _session_permanent,
                      _session_refresh_each_request):
        with self.setup_dynamodb():
            app = app_utils.create_app(
                {
                    "SESSION_TYPE": "dynamodb",
                    "SESSION_DYNAMODB": self.client,
                    "SESSION_PERMANENT": _session_permanent,
                    "SESSION_REFRESH_EACH_REQUEST": _session_refresh_each_request,
                    "PERMANENT_SESSION_LIFETIME": timedelta(seconds=5),

                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, DynamoDBSession)
                self._test_lifetime(app, _session_permanent)
