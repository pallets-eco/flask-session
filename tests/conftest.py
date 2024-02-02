import sys

sys.path.append("src")
import flask  # noqa E402
import flask_session  # noqa E402
import pytest  # noqa E402


@pytest.fixture(scope="function")
def app_utils():
    class Utils:
        def create_app(self, config_dict=None):
            app = flask.Flask(__name__)
            if config_dict:
                app.config.update(config_dict)

            @app.route("/set", methods=["POST"])
            def app_set():
                flask.session["value"] = flask.request.form["value"]
                return "value set"

            @app.route("/modify", methods=["POST"])
            def app_modify():
                flask.session["value"] = flask.request.form["value"]
                return "value set"

            @app.route("/delete", methods=["POST"])
            def app_del():
                del flask.session["value"]
                return "value deleted"

            @app.route("/get")
            def app_get():
                return flask.session.get("value")

            flask_session.Session(app)
            return app

        def test_session_set(self, app):
            client = app.test_client()
            assert client.post("/set", data={"value": "42"}).data == b"value set"
            assert client.get("/get").data == b"42"

        def test_session_modify(self, app):
            client = app.test_client()
            assert client.post("/set", data={"value": "42"}).data == b"value set"
            assert client.post("/modify", data={"value": "43"}).data == b"value set"
            assert client.get("/get").data == b"43"

        def test_session_delete(self, app):
            client = app.test_client()
            assert client.post("/set", data={"value": "42"}).data == b"value set"
            assert client.get("/get").data == b"42"
            client.post("/delete")
            assert client.get("/get").data != b"42"

        def test_session_sign(self, app):
            client = app.test_client()
            response = client.post("/set", data={"value": "42"})
            assert response.data == b"value set"
            # Check there are two parts to the cookie, the session ID and the signature
            cookies = response.headers.getlist("Set-Cookie")
            assert "." in cookies[0].split(";")[0]

    return Utils()
