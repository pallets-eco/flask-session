Getting started
-----------------
Using pip
~~~~~~~~~~~

Navigate to the project directory and run the following commands:

Create and activate a virtual environment

.. code-block:: bash

    $ python -m venv .venv
    $ source .venv/bin/activate

Install dependencies

.. code-block:: bash

    $ pip install -r requirements/dev.txt
    $ pip install -r requirements/docs.in

Install the package in editable mode

.. code-block:: bash

    $ pip install -e .

Lint the code

.. code-block:: bash

    $ ruff check --fix

Build updated documentation locally

.. code-block:: bash

    $ cd docs
    $ make html

or

.. code-block:: bash

    $ sphinx-build -b html docs docs/_build

Run the tests together or individually

.. code-block:: bash

    $ pytest tests
    $ pytest tests/test_basic.py

For easier startup and teardown of storage for testing you may use

.. code-block:: bash

    $ docker-compose up -d
    $ docker-compose down

Using rye
~~~~~~~~~~~

.. code-block:: bash

    $ rye pin 3.11
    $ rye sync


.. code-block:: bash

    $ rye run python examples/hello.py


etc.

Pull requests
--------------
Please check previous pull requests before submitting a new one.
