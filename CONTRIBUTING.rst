Getting started
-------------

Navigate to the project directory and run the following commands:

Create and activate a virtual environment
.. code-block:: text
    python -m venv .venv
    .\venv\bin\activate


Install dependencies
.. code-block:: text
    pip install -r requirements/dev.txt
    pip install -r requirements/pytest.txt


Install Memecached and Redis and activate local server (optional)
.. code-block:: text
    brew install memcached
    brew install redis


Run the tests together or individually
.. code-block:: text
    pytest tests
    pytest tests/test_basic.py


Pull requests
-------------
Please check previous pull requests before submitting a new one.