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
            app.config["SESSION_SERIALIZATION_FORMAT"] = "json"
            # app.config["SESSION_PERMANENT"] = False

            @app.route("/", methods=["GET"])
            def app_hello():
                return "hello world"

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

            @app.route("/regenerate", methods=["POST"])
            def app_regenerate():
                app.session_interface.regenerate(flask.session)
                return "value regenerated"

            @app.route("/get")
            def app_get():
                return flask.session.get("value", "no value set")

            @app.route("/get-session-id")
            def app_get_session():
                return flask.session.sid

            flask_session.Session(app)
            return app

        def test_session(self, app):
            client = app.test_client()

            # Check no value is set from previous tests
            assert client.get("/get").data not in [b"42", b"43", b"44"]

            # Check if the Vary header is not set
            rv = client.get("/")
            assert "Vary" not in rv.headers
            assert client.get("/get-session-id").data != client.get("/get-session-id").data

            # Set a value and check it

            assert client.post("/set", data={"value": "42"}).data == b"value set"
            assert client.get("/get").data == b"42"

            # Check if the Vary header is set
            rv = client.get("/get")
            assert rv.headers["Vary"] == "Cookie"
            assert client.get("/get-session-id").data == client.get(
                "/get-session-id").data

            # Modify and delete the value
            assert client.post("/modify", data={"value": "43"}).data == b"value set"
            assert client.get("/get").data == b"43"
            assert client.post("/delete").data == b"value deleted"
            assert client.get("/get").data == b"no value set"

        def test_regenerate_session(self, app):
            client = app.test_client()
            assert client.get("/get-session-id").data != client.get(
                "/get-session-id").data
            assert client.post("/set", data={"value": "42"}).data == b"value set"
            assert client.get("/get").data == b"42"
            assert client.get("/get-session-id").data == client.get(
                "/get-session-id").data
            original = client.get("/get-session-id").data
            rg = client.post("/regenerate").data

            assert client.get("/get-session-id").data != original

        def test_session_with_cookie(self, app):
            client = app.test_client()

            # Access cookies from the response to cross check with the stored session
            response = client.post("/set", data={"value": "44"})
            session_cookie = None
            for cookie in response.headers.getlist("Set-Cookie"):
                if app.config['SESSION_COOKIE_NAME'] + '=' in cookie:
                    session_cookie = cookie
                    break
            assert session_cookie.split('; ')[0].replace(
                app.config['SESSION_COOKIE_NAME'] + '=', '') == client.get(
                "/get-session-id").data.decode('utf-8')
            assert session_cookie is not None, "Session cookie was not set."
            return session_cookie

    return Utils()
