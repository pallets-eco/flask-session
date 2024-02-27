import datetime
import json
from contextlib import contextmanager
import time

import flask
from flask_session.dynamodb import DynamoDBSession
from itsdangerous import want_bytes
import boto3


class TestMongoSession:
    """This requires package: boto3"""

    @contextmanager
    def setup_dynamodb(self):
        self.client = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
        self.store = self.client.Table("FlaskSession")
        try:
            scan = self.store.scan()
            with self.store.batch_writer() as batch:
                for each in scan["Items"]:
                    batch.delete_item(
                        Key={
                            "id": each["id"],
                        }
                    )
            yield
        finally:
            scan = self.store.scan()
            with self.store.batch_writer() as batch:
                for each in scan["Items"]:
                    batch.delete_item(
                        Key={
                            "id": each["id"],
                        }
                    )
            pass

    def test_dynamodb_default(self, app_utils):
        with self.setup_dynamodb():
            app = app_utils.create_app(
                {
                    "SESSION_TYPE": "dynamodb",
                    "SESSION_DYNAMODB": self.client,
                    "SESSION_DYNAMODB_TABLE": "FlaskSession",
                }
            )

            with app.test_request_context():
                assert isinstance(flask.session, DynamoDBSession)
                app_utils.test_session(app)
