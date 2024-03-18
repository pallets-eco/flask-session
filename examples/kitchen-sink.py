from flask import Flask, session
from flask_session import Session
from redis.exceptions import RedisError

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    {
        "SESSION_TYPE": "redis",
        "SECRET_KEY": "sdfads",
        "SESSION_SERIALIZATION_FORMAT": "json",
    }
)

Session(app)


@app.route("/")
def index():
    return "No cookies in this response if it is your first visit."


@app.route("/add-apple/")
def set():
    session["apple_count"] = session.get("apple_count", 0) + 1
    return "ok"


@app.route("/get-apples/")
def get():
    result = str(session.get("apple_count", "no apples"))
    return result


@app.route("/login/")
def login():
    # Mitigate session fixation attacks
    # If the session is not empty (/add-apple/ was previously visited), the session will be regenerated
    app.session_interface.regenerate(session)
    # Here you would authenticate the user first
    session["logged_in"] = True
    return "logged in"


@app.route("/logout/")
def delete():
    session.clear()
    return "deleted"


@app.route("/error/")
def error():
    raise RedisError("An error occurred with Redis")


@app.errorhandler(RedisError)
def handle_redis_error(error):
    app.logger.error(f"Redis error encountered: {error}")
    return "A problem occurred with our Redis service. Please try again later.", 500


if __name__ == "__main__":
    app.run(debug=True)
