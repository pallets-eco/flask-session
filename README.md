<img src="https://raw.githubusercontent.com/pallets-eco/flask-session/main/docs/_static/icon/favicon-192x192.png" width="60" height="60" alt="Flask-Session">

# Flask-Session

Flask-Session is an extension for Flask that adds support for server-side sessions to your application.

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/pallets-eco/flask-session/test.yaml?logo=github)
![Documentation status](https://img.shields.io/readthedocs/flask-session?logo=readthedocs)
![BSD-3 Clause License](https://img.shields.io/github/license/pallets-eco/flask-session?logo=bsd)
![Common Changelog](https://common-changelog.org/badge.svg)
![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&label=style)
![PyPI - Latest Version](https://img.shields.io/pypi/v/flask-session.svg?logo=pypi)
![PyPI - Python Version](https://img.shields.io/badge/dynamic/json?query=info.requires_python&label=python&logo=python&url=https%3A%2F%2Fpypi.org%2Fpypi%2Fflask-session%2Fjson)
![Discord](https://img.shields.io/discord/531221516914917387?logo=discord)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-session?logo=pypi)

## Installing

Install and update using pip:

```py
$ pip install flask-session[redis]
```

You can include any supported storage type in place of redis.

## A Simple Example

```py
from flask import Flask, session
from flask_session import Session

app = Flask(__name__)
# Check Configuration section for more details
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')
```

## Supported Storage Types

-   Redis
-   Memcached
-   FileSystem
-   MongoDB
-   SQLALchemy
-   DynamoDB

## Documentation

Learn more at the official [Flask-Session Documentation](https://flask-session.readthedocs.io/en/latest/).

## Maintainers

-   [Lxstr](https://github.com/Lxstr)
-   Pallets Team

## Contribute

Thanks to all those who have contributed to Flask-Session. A full list can be found at [CONTRIBUTORS.md](https://github.com/pallets-eco/flask-session/blob/development/CONTRIBUTORS.md).

If you want to contribute, please check the [CONTRIBUTING.rst](https://github.com/pallets-eco/flask-session/blob/development/CONTRIBUTING.rst).

## Donate

The Pallets organization develops and supports Flask-Session and other popular packages. In order to grow the community of contributors and users, and allow the maintainers to devote more time to the projects, please donate today.
