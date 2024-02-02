import flask
import flask_session
import pytest


def test_tot_seconds_func():
    import datetime

    td = datetime.timedelta(days=1)
    assert flask_session.sessions.total_seconds(td) == 86400


def test_null_session():
    """Invalid session should fail to get/set the flask session"""
    app = flask.Flask(__name__)
    app.secret_key = "alsdkfjaldkjsf"
    flask_session.Session(app)

    with app.test_request_context():
        assert not flask.session.get("missing_key")
        with pytest.raises(RuntimeError):
            flask.session["foo"] = 42
        with pytest.raises(KeyError):
            print(flask.session["foo"])
