import warnings
from datetime import datetime
from datetime import timedelta as TimeDelta
from typing import Any, Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import want_bytes
from sqlalchemy import Column, DateTime, Integer, LargeBinary, Sequence, String

from .._utils import retry_query
from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults


class SqlAlchemySession(ServerSideSession):
    pass


def create_session_model(db, table_name, schema=None, bind_key=None, sequence=None):
    class Session(db.Model):
        __tablename__ = table_name
        __table_args__ = {"schema": schema} if schema else {}
        __bind_key__ = bind_key

        id = (
            Column(Integer, Sequence(sequence), primary_key=True)
            if sequence
            else Column(Integer, primary_key=True)
        )
        session_id = Column(String(255), unique=True)
        data = Column(LargeBinary)
        expiry = Column(DateTime)

        def __init__(self, session_id: str, data: Any, expiry: datetime):
            self.session_id = session_id
            self.data = data
            self.expiry = expiry

        def __repr__(self):
            return f"<Session data {self.data}>"

    return Session


class SqlAlchemySessionInterface(ServerSideSessionInterface):
    """Uses the Flask-SQLAlchemy from a flask app as session storage.

    :param app: A Flask app instance.
    :param client: A Flask-SQLAlchemy instance.
    :param key_prefix: A prefix that is added to all storage keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param serialization_format: The serialization format to use for the session data.
    :param table: The table name you want to use.
    :param sequence: The sequence to use for the primary key if needed.
    :param schema: The db schema to use.
    :param bind_key: The db bind key to use.
    :param cleanup_n_requests: Delete expired sessions on average every N requests.

    .. versionadded:: 0.7
        db changed to client to be standard on all session interfaces.
        The `cleanup_n_request` parameter was added.

    .. versionadded:: 0.6
        The `sid_length`, `sequence`, `schema` and `bind_key` parameters were added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    session_class = SqlAlchemySession
    ttl = False

    def __init__(
        self,
        app: Optional[Flask],
        client: Optional[SQLAlchemy] = Defaults.SESSION_SQLALCHEMY,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
        table: str = Defaults.SESSION_SQLALCHEMY_TABLE,
        sequence: Optional[str] = Defaults.SESSION_SQLALCHEMY_SEQUENCE,
        schema: Optional[str] = Defaults.SESSION_SQLALCHEMY_SCHEMA,
        bind_key: Optional[str] = Defaults.SESSION_SQLALCHEMY_BIND_KEY,
        cleanup_n_requests: Optional[int] = Defaults.SESSION_CLEANUP_N_REQUESTS,
    ):
        self.app = app

        if client is None or not isinstance(client, SQLAlchemy):
            warnings.warn(
                "No valid SQLAlchemy instance provided, attempting to create a new instance on localhost with default settings.",
                RuntimeWarning,
                stacklevel=1,
            )
            client = SQLAlchemy(app)
        self.client = client

        # Create the session model
        self.sql_session_model = create_session_model(
            client, table, schema, bind_key, sequence
        )
        # Create the table if it does not exist
        with app.app_context():
            if bind_key:
                engine = self.client.get_engine(app, bind=bind_key)
            else:
                engine = self.client.engine
            self.sql_session_model.__table__.create(bind=engine, checkfirst=True)

        super().__init__(
            app,
            key_prefix,
            use_signer,
            permanent,
            sid_length,
            serialization_format,
            cleanup_n_requests,
        )

    @retry_query()
    def _delete_expired_sessions(self) -> None:
        try:
            self.client.session.query(self.sql_session_model).filter(
                self.sql_session_model.expiry <= datetime.utcnow()
            ).delete(synchronize_session=False)
            self.client.session.commit()
        except Exception:
            self.client.session.rollback()
            raise

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (record) from the database
        record = self.sql_session_model.query.filter_by(session_id=store_id).first()

        # "Delete the session record if it is expired as SQL has no TTL ability
        if record and (record.expiry is None or record.expiry <= datetime.utcnow()):
            try:
                self.client.session.delete(record)
                self.client.session.commit()
            except Exception:
                self.client.session.rollback()
                raise
            record = None

        if record:
            serialized_session_data = want_bytes(record.data)
            return self.serializer.decode(serialized_session_data)
        return None

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        try:
            self.sql_session_model.query.filter_by(session_id=store_id).delete()
            self.client.session.commit()
        except Exception:
            self.client.session.rollback()
            raise

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_expiration_datetime = datetime.utcnow() + session_lifetime

        # Serialize session data
        serialized_session_data = self.serializer.encode(session)

        # Update existing or create new session in the database
        try:
            record = self.sql_session_model.query.filter_by(session_id=store_id).first()
            if record:
                record.data = serialized_session_data
                record.expiry = storage_expiration_datetime
            else:
                record = self.sql_session_model(
                    session_id=store_id,
                    data=serialized_session_data,
                    expiry=storage_expiration_datetime,
                )
                self.client.session.add(record)
            self.client.session.commit()
        except Exception:
            self.client.session.rollback()
            raise
