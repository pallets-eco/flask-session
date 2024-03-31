import flask
import flask_session
import pytest

from flask_session.mongodb import MongoDBSessionInterface


def test_null_session():
    """Invalid session should fail to get/set the flask session"""
    with pytest.raises(ValueError):
        app = flask.Flask(__name__)
        app.secret_key = "alsdkfjaldkjsf"
        flask_session.Session(app)


class CustomInterface(MongoDBSessionInterface):
    def hello(self):
        return "world"


def test_init_app_with_custom_interface():
    """Test init_app with a custom session interface"""
    app = flask.Flask(__name__)
    flask_session.Session(app, custom_interface=CustomInterface(app=app))
    assert isinstance(app.session_interface, CustomInterface)
    assert app.session_interface.hello() == "world"
