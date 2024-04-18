"""Provides a Session Interface to DynamoDB"""

import warnings
from datetime import datetime
from datetime import timedelta as TimeDelta
from decimal import Decimal
from typing import Optional

import boto3
from flask import Flask
from itsdangerous import want_bytes
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults


class DynamoDBSession(ServerSideSession):
    pass


class DynamoDBSessionInterface(ServerSideSessionInterface):
    """A Session interface that uses dynamodb as backend. (`boto3` required)

    By default (``table_exists=False``) it will create a DynamoDB table with this configuration:

    - Table Name: Value of ``table_name``, by default ``Sessions``
    - Key Schema: Simple Primary Key ``id`` of type string
    - Billing Mode: Pay per Request
    - Time to Live enabled, attribute name: ``expiration``
    - The following permissions are required:
        - ``dynamodb:CreateTable``
        - ``dynamodb:DescribeTable``
        - ``dynamodb:UpdateTimeToLive``
        - ``dynamodb:GetItem``
        - ``dynamodb:UpdateItem``
        - ``dynamodb:DeleteItem``

    If you set ``table_exists`` to True, you're responsible for creating a table with this config:

    - Table Name: Value of ``table_name``, by default ``Sessions``
    - Key Schema: Simple Primary Key ``id`` of type string
    - Time to Live enabled, attribute name: ``expiration``
    - The following permissions are required under these circumstances:
        - ``dynamodb:GetItem``
        - ``dynamodb:UpdateItem``
        - ``dynamodb:DeleteItem``

    :param client: A ``DynamoDBServiceResource`` instance, i.e. the result
                of ``boto3.resource("dynamodb", ...)``.
    :param key_prefix: A prefix that is added to all DynamoDB store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param table_name: DynamoDB table name to store the session.
    :param table_exists: The table already exists, don't try to create it (default=False).

    .. versionadded:: 0.9
        The `table_exists` parameter was added.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    session_class = DynamoDBSession

    def __init__(
        self,
        app: Flask,
        client: Optional[DynamoDBServiceResource] = Defaults.SESSION_DYNAMODB,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
        table_name: str = Defaults.SESSION_DYNAMODB_TABLE,
        table_exists: Optional[bool] = Defaults.SESSION_DYNAMODB_TABLE_EXISTS,
    ):

        # NOTE: The name client is a bit misleading as we're using the resource API of boto3 as opposed to the service API
        #       which would be instantiated as boto3.client.
        if client is None:
            warnings.warn(
                "No valid DynamoDBServiceResource instance provided, attempting to create a new instance on localhost:8000.",
                RuntimeWarning,
                stacklevel=1,
            )
            client = boto3.resource(
                "dynamodb",
                endpoint_url="http://localhost:8000",
                region_name="us-west-2",
                aws_access_key_id="dummy",
                aws_secret_access_key="dummy",
            )

        self.client = client
        self.table_name = table_name

        if not table_exists:
            self._create_table()

        self.store = client.Table(table_name)
        super().__init__(
            app,
            key_prefix,
            use_signer,
            permanent,
            sid_length,
            serialization_format,
        )

    def _create_table(self):
        try:
            self.client.create_table(
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
                ],
                TableName=self.table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            self.client.meta.client.get_waiter("table_exists").wait(
                TableName=self.table_name
            )
            self.client.meta.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={
                    "Enabled": True,
                    "AttributeName": "expiration",
                },
            )
        except (
            AttributeError,
            self.client.meta.client.exceptions.ResourceInUseException,
        ):
            # TTL already exists, or table already exists
            pass

    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (document) from the database
        document = self.store.get_item(Key={"id": store_id}).get("Item")
        session_is_not_expired = Decimal(datetime.utcnow().timestamp()) <= document.get(
            "expiration"
        )
        if document and session_is_not_expired:
            serialized_session_data = want_bytes(document.get("val").value)
            return self.serializer.loads(serialized_session_data)
        return None

    def _delete_session(self, store_id: str) -> None:
        self.store.delete_item(Key={"id": store_id})

    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_expiration_datetime = datetime.utcnow() + session_lifetime
        # Serialize the session data
        serialized_session_data = self.serializer.dumps(dict(session))

        self.store.update_item(
            Key={
                "id": store_id,
            },
            UpdateExpression="SET val = :value, expiration = :exp",
            ExpressionAttributeValues={
                ":value": serialized_session_data,
                ":exp": Decimal(storage_expiration_datetime.timestamp()),
            },
        )
