from flask import Flask, session
from flask_session import Session
from redis.exceptions import RedisError

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


if __name__ == "__main__":
    app.run(debug=True)
