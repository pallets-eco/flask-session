from __future__ import annotations

from typing import Optional

from flask import Flask
from psycopg2.pool import ThreadedConnectionPool
from datetime import timedelta as TimeDelta

from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults

DEFAULT_TABLE_NAME = "flask_sessions"
DEFAULT_SCHEMA_NAME = "public"
DEFAULT_PG_MAX_DB_CONN = 10

class PostgreSqlSession(ServerSideSession):
    pass


class PostgreSqlSessionInterface(ServerSideSessionInterface):
    pass

    session_class = PostgreSqlSession
    ttl = True


    def __init__(
        self,
        uri: str,
        *,
        app: Flask,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
        cleanup_n_requests: Optional[int] = Defaults.SESSION_CLEANUP_N_REQUESTS,
        table_name: str = DEFAULT_TABLE_NAME,
        schema_name: str = DEFAULT_SCHEMA_NAME,
        max_db_conn: int = DEFAULT_PG_MAX_DB_CONN,
    ) -> None:
        """Initialize a new Flask-PgSession instance.

        Args:
            uri (str): The database URI to connect to.
            table_name (str, optional): The name of the table to store sessions in.
                Defaults to "flask_sessions".
            schema_name (str, optional): The name of the schema to store sessions in.
                Defaults to "public".
            key_prefix (str, optional): The prefix to prepend to the session ID when
                storing it in the database. Defaults to "".
            use_signer (bool, optional): Whether to use a signer to sign the session.
                Defaults to False.
            permanent (bool, optional): Whether the session should be permanent.
                Defaults to True.
            autodelete_expired_sessions (bool, optional): Whether to automatically
                delete expired sessions. Defaults to True.
            max_db_conn (int, optional): The maximum number of database connections to
                keep open. Defaults to 10.
        """
        self.pool = ThreadedConnectionPool(1, max_db_conn, uri)

        self._table = table_name
        self._schema = schema_name

        super().__init__(
            app,
            key_prefix,
            use_signer,
            permanent,
            sid_length,
            serialization_format,
            cleanup_n_requests,
        )

        def _delete_expired_sessions(self) -> None:
            raise NotImplementedError

        def _delete_session(self, store_id:str) -> None:
            raise NotImplementedError

        def _upsert_session(self, session_lifetime:TimeDelta, session: ServerSideSession, store_id: str) -> None:
            raise NotImplementedError

        def _retrieve_session_data(self, store_id: str)-> Optional[dict]:
            raise NotImplementedError

