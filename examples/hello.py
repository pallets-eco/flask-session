from flask import Flask, session
from flask_session import Session

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    {
        "SESSION_TYPE": "sqlalchemy",
        "SQLALCHEMY_DATABASE_URI": "sqlite:////tmp/test.db",
        "SQLALCHEMY_USE_SIGNER": True,
    }
)
Session(app)


@app.route("/set/")
def set():
    session["key"] = "value"
    return "ok"


@app.route("/get/")
def get():
    import time

    start_time = time.time()
    result = session.get("key", "not set")
    print("get", (time.time() - start_time) * 1000)
    return result


if __name__ == "__main__":
    app.run(debug=True)
