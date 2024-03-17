Getting started
-----------------

Navigate to the project directory and run the following commands:

Create and activate a virtual environment

.. code-block:: bash
    
    $ python -m venv .venv
    $ source .venv/bin/activate

Install dependencies

.. code-block:: bash

    $ pip install -r requirements/dev.txt
    $ pip install -r requirements/docs.txt

Install the package in editable mode

.. code-block:: bash

    $ pip install -e .

Lint the code

.. code-block:: bash

    $ ruff check --fix

Build updated documentation

.. code-block:: bash

    $ pip install -r requirements/docs.txt
    $ cd docs
    $ make html

Run the tests together or individually

.. code-block:: bash
    
    $ pytest tests
    $ pytest tests/test_basic.py

For easier startup and teardown of storage for testing you may use 

.. code-block:: bash

    $ docker-compose up -d
    $ docker-compose down

Pull requests
--------------
Please check previous pull requests before submitting a new one.