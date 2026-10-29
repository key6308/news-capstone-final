Troubleshooting
===============

Database connection errors
--------------------------

Check that MySQL/MariaDB is running, the database exists, and ``DB_NAME``,
``DB_USER``, ``DB_PASSWORD``, ``DB_HOST``, and ``DB_PORT`` match the database.
With Docker Compose, the database host is the service name ``db`` rather than
``127.0.0.1``.

Missing Python packages
-----------------------

Activate your virtual environment and run::

   python -m pip install -r requirements.txt

Migration errors
----------------

Run ``python manage.py migrate`` after confirming the database is reachable.

Documentation build errors
--------------------------

Install the requirements first, then run::

   python -m sphinx -b html docs docs/_build/html
