import json
from contextlib import contextmanager

import flask
import aerospike
from aerospike import exception as ex
from flask_session.aerospike import AerospikeSession

from flask_session import Defaults


class TestAerospikeSession:
    """This requires package: Aerospike"""

    def setup_aerospike(self):
        self.asc = aerospike.client({'hosts': [('127.0.0.1', 3000)]}).connect()
        # try:
        #     self.mc.flush_all()
        #     yield
        # finally:
        #     self.mc.flush_all()
        #     # Memcached connections are pooled, no close needed

    def retrieve_stored_session(self, key):
        try:
            return self.asc.get((
                                 'test',
                                 key,
                                 Defaults.SESSION_AEROSPIKE_BIND_KEY))[2]
        except (ex.RecordNotFound, ex.NamespaceNotFound):
            return None



    def test_aerospike_default(self, app_utils):
        self.setup_aerospike()
        app = app_utils.create_app(
            {"SESSION_TYPE": "aerospike",
             "SESSION_AEROSPIKE": self.asc,
             'SESSION_AEROSPIKE_NAMESPACE': 'test',
             }
        )

        with app.test_request_context():
            assert isinstance(
                flask.session,
                AerospikeSession,
            )
            app_utils.test_session(app)

            # Check if the session is stored in Aerospike
            cookie = app_utils.test_session_with_cookie(app)
            session_id = cookie.split(";")[0].split("=")[1]
            stored_session = self.retrieve_stored_session(f"session:{session_id}")
            assert stored_session.get("value") == "44"
