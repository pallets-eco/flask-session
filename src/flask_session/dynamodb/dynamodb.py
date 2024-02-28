from decimal import Decimal
import warnings
from datetime import datetime
from datetime import timedelta as TimeDelta
from typing import Optional
from mypy_boto3_dynamodb import DynamoDBServiceResource
import boto3

try:
    import cPickle as pickle
except ImportError:
    import pickle

from datetime import datetime, timezone

from itsdangerous import want_bytes

from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults


class DynamoDBSession(ServerSideSession):
    pass


class DynamoDBSessionInterface(ServerSideSessionInterface):
    """A Session interface that uses dynamodb as backend. (`boto3` required)

    :param client: A ``DynamoDBServiceResource`` instance.
    :param key_prefix: A prefix that is added to all DynamoDB store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param table_name: DynamoDB table name to store the session.
    :param url: DynamoDB URL for local testing.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    serializer = pickle
    session_class = DynamoDBSession

    def __init__(
        self,
        client: Optional[DynamoDBServiceResource] = Defaults.SESSION_DYNAMODB,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_SID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
        table_name: str = Defaults.SESSION_DYNAMODB_TABLE,
        url: str = Defaults.SESSION_DYNAMODB_URL,
    ):
        if client is None:
            warnings.warn(
                "No valid DynamoDBServiceResource instance provided, attempting to create a new instance on localhost:8000.",
                RuntimeWarning,
                stacklevel=1,
            )
            client = boto3.resource("dynamodb", endpoint_url=url)
        try:
            client.meta.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={
                    "Enabled": True,
                    "AttributeName": "expiration",
                },
            )
        except AttributeError:
            pass

        self.client = client
        self.store = client.Table(table_name)
        super().__init__(self.store, key_prefix, use_signer, permanent, sid_length)

    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (document) from the database
        document = self.store.get_item(Key={"id": store_id})["Item"]
        if document:
            serialized_session_data = want_bytes(document["val"].value)
            return self.serializer.decode(serialized_session_data)
        return None

    def _delete_session(self, store_id: str) -> None:
        self.store.delete_item(Key={"id": store_id})

    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_expiration_datetime = datetime.utcnow() + session_lifetime
        # Serialize the session data
        serialized_session_data = self.serializer.encode(session)
        print(storage_expiration_datetime.timestamp())

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
