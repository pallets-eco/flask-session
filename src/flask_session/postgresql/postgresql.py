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
    """A Session interface that uses PostgreSQL as a session storage. (`psycopg2` required)

    :param pool: A ``psycopg2.pool.ThreadedConnectionPool`` instance.
    :param key_prefix: A prefix that is added to all storage keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param serialization_format: The serialization format to use for the session data.
    :param table: The table name you want to use.
    :param schema: The db schema to use.
    :param cleanup_n_requests: Delete expired sessions on average every N requests.
    """

    session_class = PostgreSqlSession
    ttl = False

    def __init__(
        self,
        app: Flask,
        pool: ThreadedConnectionPool | None = Defaults.SESSION_POSTGRESQL,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
        table: str = Defaults.SESSION_POSTGRESQL_TABLE,
        schema: str = Defaults.SESSION_POSTGRESQL_SCHEMA,
        cleanup_n_requests: int | None = Defaults.SESSION_CLEANUP_N_REQUESTS,
    ) -> None:
        if not isinstance(pool, ThreadedConnectionPool):
            raise TypeError("No valid ThreadedConnectionPool instance provided.")

        self.pool = pool

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
                dict(session_id=store_id),
            )

    @retry_query(max_attempts=3)
    def _retrieve_session_data(self, store_id: str) -> dict | None:
        with self._get_cursor() as cur:
            cur.execute(
                self._queries.retrieve_session_data,
                dict(session_id=store_id),
            )
            session_data = cur.fetchone()

        if session_data is not None:
            serialized_session_data = want_bytes(session_data[0])
            return self.serializer.decode(serialized_session_data)
        return None

    @retry_query(max_attempts=3)
    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:

        serialized_session_data = self.serializer.encode(session)

        if session.sid is not None:
            assert session.sid == store_id.removeprefix(self.key_prefix)

        with self._get_cursor() as cur:
            cur.execute(
                self._queries.upsert_session,
                dict(
                    session_id=store_id,
                    data=serialized_session_data,
                    ttl=session_lifetime,
                ),
            )

    def _drop_table(self):
        with self._get_cursor() as cur:
            cur.execute(self._queries.drop_sessions_table)
