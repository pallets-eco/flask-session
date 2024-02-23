import flask
import flask_session
import pytest


def test_null_session():
    """Invalid session should fail to get/set the flask session"""
    with pytest.raises(ValueError):
        app = flask.Flask(__name__)
        app.secret_key = "alsdkfjaldkjsf"
        flask_session.Session(app)
