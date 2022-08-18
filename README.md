<h1 align="center">
  <br>
  <img src="https://github.com/christopherpickering/flask-session2/raw/master/resources/flask-session.png" alt="logo" width="370" />
  <br>
</h1>

<h4 align="center">Adds support for Server-side Session to your <a href="https://flask.palletsprojects.com">Flask</a> application.</h4>

<p align="center">
<a href="https://codecov.io/gh/christopherpickering/flask-session2" >  <img src="https://codecov.io/gh/christopherpickering/flask-session2/branch/master/graph/badge.svg?token=97G1F34PKY"/>  </a>
  <a href="https://www.codacy.com/gh/christopherpickering/flask-session2/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=christopherpickering/flask-session2&amp;utm_campaign=Badge_Grade"><img src="https://app.codacy.com/project/badge/Grade/4f05bcca902448b1aecacc51aa94d363"/></a>
<a href="https://pepy.tech/project/flask-session2">
     <img src="https://pepy.tech/badge/flask-session2" alt="Downloads">
   </a>
 <a href="https://pypi.org/project/flask-session2/">
     <img src="https://img.shields.io/pypi/v/flask-session2" alt="Pypi Download">
   </a>
</p>


## Installation

Install the extension with the following command::

```bash
pip install Flask-Session2
```

## Quickstart

Flask-Session is really easy to use.

Basically for the common use of having one Flask application all you have to do is to create your Flask application, load the configuration of choice and
then create the `Session` object by passing it the application.

The `Session` instance is not used for direct access, you should always use `flask.session`:

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

You may also set up your application later using `Session.init_app` method:

```py
sess = Session()
sess.init_app(app)
```

## Configuration

The following configuration values exist for Flask-Session.  Flask-Session loads these values from your Flask application config, so you should configure
your app first before you pass it to Flask-Session.  Note that these values cannot be modified after the ``init_app`` was applied so make sure to not modify them at runtime.

We are not supplying something like `SESSION_REDIS_HOST` and `SESSION_REDIS_PORT`, if you want to use the `RedisSessionInterface`, you should configure `SESSION_REDIS` to your own `redis.Redis` instance. This gives you more flexibility, like maybe you want to use the same `redis.Redis` instance for cache purpose too, then you do not need to keep two `redis.Redis` instance in the same process.

The following configuration values are builtin configuration values within Flask itself that are related to session.  **They are all understood by
Flask-Session, for example, you should use PERMANENT_SESSION_LIFETIME to control your session lifetime.**

| Name | Description |
|--|--|
|`SESSION_COOKIE_NAME`          | the name of the session cookie         |
|`SESSION_COOKIE_DOMAIN`        | the domain for the session cookie.  If this is not set, the cookie will be valid for all subdomains of `SERVER_NAME`. |
|`SESSION_COOKIE_PATH`          | the path for the session cookie.  If this is not set the cookie will be valid for all of `APPLICATION_ROOT` or if that is not set for `'/'`. |
|`SESSION_COOKIE_HTTPONLY`      | controls if the cookie should be set with the httponly flag.  Defaults to `True`. |
|`SESSION_COOKIE_SECURE`        | controls if the cookie should be set with the secure flag.  Defaults to `False`. |
|`PERMANENT_SESSION_LIFETIME`   | the lifetime of a permanent session as :class:`datetime.timedelta` object. Starting with Flask 0.8 this can also be an integer representing seconds. |


A list of configuration keys also understood by the extension:

| Name | Description |
|--|--|
| `SESSION_TYPE`            |  Specifies which type of session interface to use.  Built-in session types:<br>- **null**: NullSessionInterface (default) <br> - **redis**: RedisSessionInterface <br> - **memcached**: MemcachedSessionInterface <br> - **filesystem**: FileSystemSessionInterface <br> - **mongodb**: MongoDBSessionInterface <br> - **sqlalchemy**: SqlAlchemySessionInterface <br> - **elasticsearch**: ElasticsearchSessionInterface <br> - **datastore**: GoogleCloudDatastoreSessionInterface <br> - **firestore**: GoogleFireStoreSessionInterface <br> - **peewee**: PeeweeSessionInterface <br> - **dynamodb**: DynamoDBSessionInterface |
| `SESSION_PERMANENT`       |  Whether use permanent session or not, default to be `True` |
| `SESSION_USE_SIGNER`      |  Whether sign the session cookie sid or not, if set to `True`, you have to set :attr:`flask.Flask.secret_key`, default to be `False` |
| `SESSION_KEY_PREFIX`      |  A prefix that is added before all session keys. This makes it possible to use the same backend storage server for different apps, default "session:" |


Basically you only need to configure `SESSION_TYPE`.

    By default, all non-null sessions in Flask-Session are permanent.

## Built-in Session Interfaces

### `NullSessionInterface`

If you do not configure a different ``SESSION_TYPE``, this will be used to
generate nicer error messages.  Will allow read-only access to the empty
session but fail on setting.

### `RedisSessionInterface`

Uses the Redis key-value store as a session backend. ([redis-py](https://github.com/andymccurdy/redis-py) required)

| Name | Description |
|--|--|
| `SESSION_REDIS`           |  A `redis.Redis` instance, default connect to `127.0.0.1:6379` |

### `MemcachedSessionInterface`

Uses the Memcached as a session backend. ([pymemecache](https://pypi.org/project/pymemcache/) required)

| Name | Description |
|--|--|
| `SESSION_MEMCACHED`       |  A `memcache.Client` instance, default connect to `127.0.0.1:11211` |

### `FileSystemSessionInterface`

Uses the `cachelib.file.FileSystemCache` as a session backend.

| Name | Description |
|--|--|
| `SESSION_FILE_DIR`        |  The directory where session files are stored. Default to use `flask_session` directory under current working directory. |
| `SESSION_FILE_THRESHOLD`  |  The maximum number of items the session stores before it starts deleting some, default 500 |
| `SESSION_FILE_MODE`       |  The file mode wanted for the session files, default 0600 |


### `MongoDBSessionInterface`

Uses the MongoDB as a session backend. ([pymongo](http://api.mongodb.org/python/current/index.html) required)

| Name | Description |
|--|--|
| `SESSION_MONGODB`         |  A `pymongo.MongoClient` instance, default connect to `127.0.0.1:27017` |
| `SESSION_MONGODB_DB`      |  The MongoDB database you want to use, default "flask_session" |
| `SESSION_MONGODB_COLLECT` |  The MongoDB collection you want to use, default "sessions" |

### `SqlAlchemySessionInterface`

Uses SQLAlchemy as a session backend. ([Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy/) required)

| Name | Description |
|--|--|
| `SESSION_SQLALCHEMY`      |  A `flask_sqlalchemy.SQLAlchemy` instance whose database connection URI is configured using the `SQLALCHEMY_DATABASE_URI` parameter |
| `SESSION_SQLALCHEMY_TABLE`|  The name of the SQL table you want to use, default "sessions" |
| SESSION_AUTODELETE        |  Auto remove old sessions from database |

### `ElasticsearchSessionInterface`

Uses elasticsearch as a session backend. ([elasticsearch](https://elasticsearch-py.readthedocs.io/en/v8.3.3/) required)

- SESSION_ELASTICSEARCH
- SESSION_ELASTICSEARCH_HOST
- SESSION_ELASTICSEARCH_INDEX

### `GoogleCloudDatastoreSessionInterface`

Uses Google Cloud Datastore as a session backend. ([google-cloud-datastore](https://github.com/googleapis/python-datastore) required)

- GCLOUD_APP_PROJECT_ID

### `GoogleFireStoreSessionInterface`

Uses Google Firebase as a session backend. ([google-cloud-firestore](https://pypi.org/project/google-cloud-firestore/) required)

- SESSION_FIRESTORE
- SESSION_FIRESTORE_COLLECT


### `PeeweeSessionInterface`

Uses Peewee as a session backend. ([peewee](https://pypi.org/project/peewee/) required)

- SESSION_PEEWEE_TABLE
- SESSION_PEEWEE_CONFIG

### `DynamoDBSessionInterface`

Uses DynamoDB as a session backend. ([boto3](https://pypi.org/project/boto3/) required)

| Name | Description |
|---|---|
| `SESSION_DYNAMODB`          | A `boto3.Session` instance, default creates an instance with credentials in environment variables or in the local aws config. |
| `SESSION_DYNAMODB_KEY_ID`   | The AWS key id for connecting to Dynamo. Uses environment variable or local config if not set. |
| `SESSION_DYNAMODB_ENDPOINT` | The AWS DynamoDB endpoint_url. Default is none, primarily used for local DynamoDB config. |
| `SESSION_DYNAMODB_SECRET`   | The AWS secret access key for connecting to Dynamo. Uses environment variable or local config if not set. |
| `SESSION_DYNAMODB_REGION`   | The region where the dynamodb table is located. Uses environment variable or the local config if not set. |
| `SESSION_DYNAMODB_TABLE`    | The name of the table in DyanmoDB to store session data. Default is "sessions". |

## Credits

This project is a fork of [flask-session](https://github.com/fengsp/flask-session), created by [Shipeng Feng](https://github.com/fengsp).

### Contributors

Thanks for many who have contributed to this project. Submit a PR if you have contributed and your name is missing.

- [sulantha2006](https://github.com/sulantha2006) | Google Cloud Firestore session backend
- [bsmar](https://github.com/bsmar), [Nilkree](https://github.com/Nilkree), [km445](https://github.com/km445), [PavelTsaritsynKS](https://github.com/PavelTsaritsynKS), [PetruninAleksey](https://github.com/PetruninAleksey) | Peewee session backend
- [JimBroad](https://github.com/JimBroad) | DynamoDB session backend
- [bieli](https://github.com/bieli) | Custom session backend
- [jesserobles](https://github.com/jesserobles) | Elasticsearch session backend
- [ghost](https://github.com/ghost) | Google Datastore session backend
- [PjrCodes](https://github.com/PjrCodes)
- [treycucco](https://github.com/treycucco)
- [tassaron](https://github.com/tassaron)
- [rsyring](https://github.com/rsyring)
- [Junzki](https://github.com/Junzki)
- [gdoumenc](https://github.com/gdoumenc)
- [twolfson](https://github.com/twolfson)
- [splbio](https://github.com/splbio)
- [moskitos80](https://github.com/moskitos80)
- [h4ck3rm1k3](https://github.com/h4ck3rm1k3)
- [grutz](https://github.com/grutz)
- [zebpalmer](https://github.com/zebpalmer)
- [knivre](https://github.com/knivre)
- [funoverip](https://github.com/funoverip)
- [isopropanol](https://github.com/isopropanol)
- [ronsmith](https://github.com/ronsmith)
- [marcuspen](https://github.com/marcuspen)
- [lucassus](https://github.com/lucassus)
- [loukash](https://github.com/loukash)
- [najamansari](https://github.com/najamansari)
- [brunokim](https://github.com/brunokim)
- [Ricky-Hao](https://github.com/Ricky-Hao)
- [slastrina](https://github.com/slastrina)
- [Kolarovski](https://github.com/Kolarovski)
- [wangsha](https://github.com/wangsha)
- [christopherpickering](https://github.com/christopherpickering)
