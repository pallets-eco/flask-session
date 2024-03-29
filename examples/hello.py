from flask import Flask, session
from flask_session import Session

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    {
        "SESSION_TYPE": "redis",
    }
)
Session(app)


@app.route("/set/")
def set():
    session["key"] = "value"
    return "ok"


@app.route("/get/")
def get():
    result = session.get("key", "not set")
    return result


@app.route("/delete/")
def delete():
    del session["key"]
    return "deleted"


@app.route("/")
def hello():
    return "hello world"


if __name__ == "__main__":
    app.run(debug=True)
