from flask import Flask, session
from flask_server_session import ServerSession
from pymongo import MongoClient

app = Flask(__name__)

# Configure the secret key for session encryption
app.config['SECRET_KEY'] = 'thisisasecretkeywow'

# Configure the MongoDB client
client = MongoClient('mongodb://localhost:27017')

# Configure the session type as MongoDB
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = client
#app.config["SESSION_MONGODB_DB"] = 'testing'
#app.config["SESSION_MONGODB_COLLECTION"] = 'sessions'

# Initialize the Flask-Session extension
ServerSession(app)

@app.route('/')
def index():
    if not session.get('username'):
        session['username'] = 'default'

    # Retrieve the value from the session
    username = session.get('username')

    return f'Hello, {username}!'

@app.route('/delete')
def delete():
    # Clear the session
    session.clear()

    return 'Session cleared!'

@app.route('/change/<username>')
def change(username):
    # Change the session username
    session['username'] = username

    return f'Changed session username to {username}!'

if __name__ == '__main__':
    app.run()
