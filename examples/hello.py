from flask import Flask, session
from flask_session import Session
from redis.exceptions import RedisError

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    {
        "SESSION_TYPE": "redis",
        "FLASK_ENV": "production",
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
    # del session["key"]
    raise RedisError("test")
    return "deleted"


@app.errorhandler(RedisError)
def handle_redis_error(error):
    app.logger.error(f"Redis error encountered: {error}")
    return "A problem occurred with our Redis service. Please try again later.", 500


if __name__ == "__main__":
    app.run(debug=True)
