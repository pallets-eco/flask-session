import json
from contextlib import contextmanager

import flask
import pytest
from psycopg2.pool import ThreadedConnectionPool
from sqlalchemy import text

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

    def test_postgres(self, app_utils):
        with self.setup_postgresql(app_utils), self.app.test_request_context():
            assert isinstance(flask.session, PostgreSqlSession)
            app_utils.test_session(self.app)
