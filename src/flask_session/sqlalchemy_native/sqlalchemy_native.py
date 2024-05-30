from datetime import datetime
from datetime import timedelta as TimeDelta
from typing import Optional

from flask import Flask
from itsdangerous import want_bytes
from sqlalchemy import (
    Column,
    DateTime,
    Engine,
    Integer,
    LargeBinary,
    Sequence,
    String,
    delete,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Session

from .._utils import retry_query
from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults


class NativeSqlAlchemySession(ServerSideSession):
    pass


class Base(DeclarativeBase):
    pass


def create_session_model(table_name, schema=None, bind_key=None, sequence=None):
    class Session(Base):
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

        def __repr__(self):
            return f"<Session data {self.data}>"

    return Session


class NativeSqlAlchemySessionInterface(ServerSideSessionInterface):
    """Uses a SQLAlchemy engine as session storage.

    :param app: A Flask app instance.
    :param engine: A SQLAlchemy engine instance.
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
    """

    session_class = NativeSqlAlchemySession
    ttl = False

    def __init__(
        self,
        app: Optional[Flask],
        engine: Optional[Engine] = Defaults.SESSION_SQLALCHEMY_ENGINE,
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

        if engine is None or not isinstance(engine, Engine):
            raise TypeError("No valid Engine instance provided.")
        self.engine = engine

        # Create the session model
        self.sql_session_model = create_session_model(
            table, schema, bind_key, sequence
        )
        # Create the table if it does not exist
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
        with Session(self.engine) as session:
            session.execute(
                delete(self.sql_session_model)
                .where(self.sql_session_model.expiry <= datetime.utcnow()),
                execution_options={"synchronize_session": False}
            )
            session.commit()

    @retry_query()
    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (record) from the database
        with Session(self.engine) as session:
            record = session.scalars(
                select(self.sql_session_model)
                .where(self.sql_session_model.session_id == store_id)
            ).first()

        # "Delete the session record if it is expired as SQL has no TTL ability
        if record and (record.expiry is None or record.expiry <= datetime.utcnow()):
            with Session(self.engine) as session:
                session.delete(record)
                session.commit()
            record = None

        if record:
            serialized_session_data = want_bytes(record.data)
            return self.serializer.loads(serialized_session_data)
        return None

    @retry_query()
    def _delete_session(self, store_id: str) -> None:
        with Session(self.engine) as session:
            session.execute(
                delete(self.sql_session_model)
                .where(self.sql_session_model.session_id == store_id)
            )
            session.commit()

    @retry_query()
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_expiration_datetime = datetime.utcnow() + session_lifetime

        # Serialize session data
        serialized_session_data = self.serializer.dumps(dict(session))

        # Update existing or create new session in the database
        with Session(self.engine) as session:
            record = session.scalars(
                select(self.sql_session_model)
                .where(self.sql_session_model.session_id == store_id)
            ).first()

            if record:
                record.data = serialized_session_data
                record.expiry = storage_expiration_datetime
            else:
                record = self.sql_session_model(
                    session_id=store_id,
                    data=serialized_session_data,
                    expiry=storage_expiration_datetime,
                )
                session.add(record)
            session.commit()
