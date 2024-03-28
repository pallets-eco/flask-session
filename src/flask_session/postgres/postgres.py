from __future__ import annotations

from contextlib import contextmanager
from datetime import timedelta as TimeDelta
from typing import Generator

from flask import Flask
from itsdangerous import want_bytes
from psycopg2.extensions import connection as PsycoPg2Connection
from psycopg2.extensions import cursor as PsycoPg2Cursor
from psycopg2.pool import ThreadedConnectionPool

from .._utils import retry_query
from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults
from ._queries import Queries


class PostgreSqlSession(ServerSideSession):
    pass


class PostgreSqlSessionInterface(ServerSideSessionInterface):
    pass

    session_class = PostgreSqlSession
    ttl = False

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
        cleanup_n_requests: int | None = Defaults.SESSION_CLEANUP_N_REQUESTS,
        table: str = Defaults.SESSION_POSTGRESQL_TABLE,
        schema: str = Defaults.SESSION_POSTGRESQL_SCHEMA,
        max_db_conn: int = Defaults.SESSION_POSTGRESQL_MAX_DB_CONN,
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

        self._table = table
        self._schema = schema

        self._queries = Queries(schema=self._schema, table=self._table)

        self._create_schema_and_table()

        super().__init__(
            app,
            key_prefix,
            use_signer,
            permanent,
            sid_length,
            serialization_format,
            cleanup_n_requests,
        )

    @contextmanager
    def _get_cursor(
        self, conn: PsycoPg2Connection | None = None
    ) -> Generator[PsycoPg2Cursor, None, None]:
        _conn: PsycoPg2Connection = conn or self.pool.getconn()

        assert isinstance(_conn, PsycoPg2Connection)
        try:
            with _conn, _conn.cursor() as cur:
                yield cur
        except Exception:
            raise
        finally:
            self.pool.putconn(_conn)

    @retry_query(max_attempts=3)
    def _create_schema_and_table(self) -> None:
        with self._get_cursor() as cur:
            cur.execute(self._queries.create_schema)
            cur.execute(self._queries.create_table)

    def _delete_expired_sessions(self) -> None:
        """Delete all expired sessions from the database."""
        with self._get_cursor() as cur:
            cur.execute(self._queries.delete_expired_sessions)

    @retry_query(max_attempts=3)
    def _delete_session(self, store_id: str) -> None:
        with self._get_cursor() as cur:
            cur.execute(
                self._queries.delete_session,
                dict(session_id=self._get_store_id(store_id)),
            )

    @retry_query(max_attempts=3)
    def _retrieve_session_data(self, store_id: str) -> dict | None:
        with self._get_cursor() as cur:
            cur.execute(
                self._queries.retrieve_session_data,
                dict(session_id=self._get_store_id(store_id)),
            )
            session_data = cur.fetchone()

        if session_data is not None:
            serialized_session_data = want_bytes(session_data)
            return self.serializer.decode(serialized_session_data)
        return None

    @retry_query(max_attempts=3)
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:

        serialized_session_data = self.serializer.encode(session)

        if session.sid is not None:
            assert session.sid == store_id

        with self._get_cursor() as cur:
            cur.execute(
                self._queries.upsert_session,
                dict(
                    session_id=store_id,
                    data=serialized_session_data,
                    ttl=session_lifetime,
                ),
            )
