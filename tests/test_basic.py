import flask
import flask_session
import pytest


def test_tot_seconds_func():
    import datetime

    td = datetime.timedelta(days=1)
    assert flask_session.sessions.total_seconds(td) == 86400


def test_null_session():
    """Invalid session should fail to get/set the flask session"""
    with pytest.raises(ValueError):
        app = flask.Flask(__name__)
        app.secret_key = "alsdkfjaldkjsf"
        flask_session.Session(app)
