import json
from decimal import Decimal
from contextlib import contextmanager
from datetime import timedelta, datetime

import boto3
import flask
import pytest
from flask_session.defaults import Defaults
from flask_session.dynamodb import DynamoDBSession
from itsdangerous import want_bytes

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

    def retrieve_stored_session(self, key, app):
        document = self.store.get_item(Key={"id": key}).get("Item")
        if document and Decimal(datetime.utcnow().timestamp()) <= document.get(
            "expiration"
        ):
            serialized_session_data = want_bytes(document.get("val").value)
            return json.loads(want_bytes(serialized_session_data)) if serialized_session_data else {}
        return None

    def test_dynamodb_with_existing_table(self, app_utils):
        """
        Setting the SESSION_DYNAMODB_TABLE_EXISTS to True for an
        existing table shouldn't change anything.
        """
        with self.setup_dynamodb():
            app = app_utils.create_app(
                {
                    "SESSION_TYPE": "dynamodb",
                    "SESSION_DYNAMODB": self.client,
                    "SESSION_DYNAMODB_TABLE_EXISTS": True,
                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, DynamoDBSession)
                self._default_test(app_utils, app)

    def test_dynamodb_with_existing_table_fails_if_table_doesnt_exist(self, app_utils):
        """Accessing a non-existent table should result in problems."""

        app = app_utils.create_app(
            {
                "SESSION_TYPE": "dynamodb",
                "SESSION_DYNAMODB": boto3.resource(
                    "dynamodb",
                    endpoint_url="http://localhost:8000",
                    region_name="us-west-2",
                    aws_access_key_id="dummy",
                    aws_secret_access_key="dummy",
                ),
                "SESSION_DYNAMODB_TABLE": "non-existent-123",
                "SESSION_DYNAMODB_TABLE_EXISTS": True,
            }
        )
        with app.test_request_context(), pytest.raises(AssertionError):
            assert isinstance(flask.session, DynamoDBSession)
            self._default_test(app_utils, app)


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
                    "PERMANENT_SESSION_LIFETIME": timedelta(seconds=4),

                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, DynamoDBSession)
                self._test_lifetime(app, _session_permanent)
