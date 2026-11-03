Installation
============

You can run the application in two ways:

* :ref:`Locally <local-install>` with Python and your own MySQL/MariaDB server.
* :ref:`With Docker <docker-install>`, which starts the app and a MariaDB
  database together.

Get the project
---------------

Clone the repository and open the project folder:

.. code-block:: powershell

   git clone https://github.com/key6308/news-capstone-consolidation.git
   cd news-capstone-consolidation

.. _local-install:

Option A: run locally
---------------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.12
* A running MySQL or MariaDB server

1. Create a virtual environment and install dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Windows PowerShell:

.. code-block:: powershell

   py -3.12 -m venv .venv          # or: python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt

If PowerShell refuses to run ``Activate.ps1``, allow scripts for the current
terminal only and try again:

.. code-block:: powershell

   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1

macOS / Linux:

.. code-block:: bash

   python3.12 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt

2. Create the database
~~~~~~~~~~~~~~~~~~~~~~

In MySQL or MariaDB, create a database and a user that can access it:

.. code-block:: sql

   CREATE DATABASE news_capstone CHARACTER SET utf8mb4;
   CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'choose-a-password';
   GRANT ALL PRIVILEGES ON news_capstone.* TO 'news_user'@'localhost';
   GRANT ALL PRIVILEGES ON `test_news_capstone`.* TO 'news_user'@'localhost';
   FLUSH PRIVILEGES;

The second ``GRANT`` lets ``python manage.py test`` create and delete its
temporary ``test_news_capstone`` database.

.. note::

   MariaDB is recommended. MySQL 8 uses ``caching_sha2_password``
   authentication, which the PyMySQL driver only supports when the
   ``cryptography`` package is installed. With MySQL 8, also run
   ``python -m pip install cryptography``.

3. Configure environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The settings module reads its configuration from environment variables. The
file ``.env.example`` lists them all:

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - Variable
     - Default
     - Purpose
   * - ``DJANGO_SECRET_KEY``
     - ``dev-only-change-me``
     - Django secret key. Set your own value outside local testing.
   * - ``DJANGO_DEBUG``
     - ``True``
     - Debug mode.
   * - ``ALLOWED_HOSTS``
     - ``127.0.0.1,localhost``
     - Comma-separated host names the site may be served on.
   * - ``DB_NAME``
     - ``news_capstone``
     - Database name.
   * - ``DB_USER``
     - ``news_user``
     - Database user.
   * - ``DB_PASSWORD``
     - ``change-me``
     - Database password.
   * - ``DB_HOST`` / ``DB_PORT``
     - ``127.0.0.1`` / ``3306``
     - Database server address.
   * - ``APPROVED_API_URL``
     - ``http://127.0.0.1:8000/api/approved/``
     - Endpoint called when an editor approves an article.

Generate a secret key with the virtual environment active:

.. code-block:: bash

   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Then set the variables in **one** of these ways.

**a) A** ``.env`` **file (recommended).** Copy the example file, then edit
``.env`` and set ``DJANGO_SECRET_KEY`` and ``DB_PASSWORD``. The settings
module loads ``.env`` from the project root with ``python-dotenv`` (installed
from ``requirements.txt``). Git ignores ``.env``.

.. code-block:: powershell

   Copy-Item .env.example .env      # Windows PowerShell

.. code-block:: bash

   cp .env.example .env             # macOS / Linux

**b) The terminal.** Variables set this way last until the terminal is
closed and override values in ``.env``. Windows PowerShell:

.. code-block:: powershell

   $env:DJANGO_SECRET_KEY = "paste-the-generated-key-here"
   $env:DB_PASSWORD = "choose-a-password"

macOS / Linux:

.. code-block:: bash

   export DJANGO_SECRET_KEY="paste-the-generated-key-here"
   export DB_PASSWORD="choose-a-password"

.. warning::

   Never commit real passwords, secret keys, or API tokens to the repository.

4. Migrate, test, and run
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   python manage.py check
   python manage.py migrate
   python manage.py test
   python manage.py runserver

Open http://127.0.0.1:8000/ in a browser. Continue with :doc:`quickstart`.

The public registration page creates reader and journalist accounts only. To
create an editor, run ``python manage.py createsuperuser``, sign in at
``/admin/``, and set the user's *Role* to *Editor*.

.. _docker-install:

Option B: run with Docker
-------------------------

Install Docker Desktop (or Docker Engine with the Compose plugin) and make
sure it is running. From the project root:

.. code-block:: powershell

   docker compose up --build

Compose starts a MariaDB container, waits until it is healthy, runs the
migrations, and starts Django on http://127.0.0.1:8000/.

To create demo data inside the running container:

.. code-block:: powershell

   docker compose exec web python manage.py seed_demo

Stop the services with :kbd:`Ctrl+C` and then:

.. code-block:: powershell

   docker compose down        # keep the database data
   docker compose down -v     # also delete the database volume

.. note::

   ``compose.yaml`` contains local-development fallback passwords. Set your
   own ``DB_PASSWORD``, ``DB_ROOT_PASSWORD``, and ``DJANGO_SECRET_KEY``
   before using it anywhere other than your own computer.
