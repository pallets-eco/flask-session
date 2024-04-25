from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timezone

import time
from tests.utils import session_permanent, session_refresh_each_request


class ABSTestSession(ABC):

    @contextmanager
    def setup_filesystem(self):
        raise NotImplementedError

    @abstractmethod
    def retrieve_stored_session(self, key, app):
        raise NotImplementedError

    @session_permanent
    @session_refresh_each_request
    def test_default(self, app_utils,_session_permanent,
                                     _session_refresh_each_request):
        raise NotImplementedError

    def _default_test(self, app_utils, app):
        app_utils.test_session(app)
        app_utils.test_regenerate_session(app)

        # Check if the session is stored in the filesystem
        cookie = app_utils.test_session_with_cookie(app)
        session_id = cookie.split(";")[0].split("=")[1]
        stored_session = self.retrieve_stored_session(f"session:{session_id}", app)
        assert stored_session.get("value") == "44"

    @session_permanent
    @session_refresh_each_request
    def test_lifetime(self, app_utils,
                                 _session_permanent,
                                 _session_refresh_each_request):
        raise NotImplementedError

    def _test_lifetime(self, app, _session_permanent):
        client = app.test_client()

        response = client.post("/set", data={"value": "44"})

        if _session_permanent is False:
            assert "Expires" not in response.headers.getlist("Set-Cookie")[0]
            return

        datetime_expires_by_cookies = datetime.strptime(
            response.headers.getlist("Set-Cookie")[0].split(";")[1].split("=")[
                1],
            "%a, %d %b %Y %H:%M:%S GMT")
        assert datetime_expires_by_cookies.replace(
            tzinfo=timezone.utc) > datetime.utcnow().replace(
            tzinfo=timezone.utc)
        session_id = client.get("/get-session-id").data
        assert self.retrieve_stored_session(
            f"session:{session_id.decode('utf-8')}", app).get("value") == "44"
        time.sleep(5)
        assert not self.retrieve_stored_session(
            f"session:{session_id.decode('utf-8')}", app)
        assert client.get("/get-session-id").data != session_id
        assert datetime_expires_by_cookies.replace(
            tzinfo=timezone.utc) < datetime.utcnow().replace(
            tzinfo=timezone.utc)

