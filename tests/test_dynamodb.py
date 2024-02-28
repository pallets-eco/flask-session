import datetime
import json
from contextlib import contextmanager
import time

import flask
from flask_session.defaults import Defaults
from flask_session.dynamodb import DynamoDBSession
from itsdangerous import want_bytes
import boto3


class TestDynamoDBSession:
    """This requires package: boto3"""

    @contextmanager
    def setup_dynamodb(self):
        self.client = boto3.resource(
            "dynamodb", endpoint_url=Defaults.SESSION_DYNAMODB_URL
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
