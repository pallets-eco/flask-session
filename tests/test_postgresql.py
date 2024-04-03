import json
from contextlib import contextmanager

import flask
from itsdangerous import want_bytes
from psycopg2.pool import ThreadedConnectionPool

from flask_session.postgres import PostgreSqlSession

TEST_DB = "postgresql://root:pwd@localhost:5433/dummy"


class TestPostgreSql:
    """This requires package: sqlalchemy"""

    @contextmanager
    def setup_postgresql(self, app_utils):
        self.pool = ThreadedConnectionPool(1, 5, TEST_DB)
        self.app = app_utils.create_app(
            {"SESSION_TYPE": "postgresql", "SESSION_POSTGRESQL": self.pool}
        )

        yield
        self.app.session_interface._drop_table()

    def retrieve_stored_session(self, key):
        with self.app.session_interface._get_cursor() as cur:
            cur.execute(
                self.app.session_interface._queries.retrieve_session_data,
                dict(session_id=key),
            )

            session_data = cur.fetchone()
        if session_data is not None:
            return want_bytes(session_data[0].tobytes())
        return None

    def test_postgres(self, app_utils):
        with self.setup_postgresql(app_utils), self.app.test_request_context():
            assert isinstance(flask.session, PostgreSqlSession)
            app_utils.test_session(self.app)

            # Check if the session is stored in MongoDB
            cookie = app_utils.test_session_with_cookie(self.app)
            session_id = cookie.split(";")[0].split("=")[1]
            byte_string = self.retrieve_stored_session(f"session:{session_id}")
            stored_session = (
                json.loads(byte_string.decode("utf-8")) if byte_string else {}
            )
            assert stored_session.get("value") == "44"
