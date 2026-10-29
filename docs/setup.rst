Setup and running
=================

Prerequisites
-------------

For local setup, install Python 3.12 and a MySQL/MariaDB server. For container
setup, install Docker Desktop or Docker Engine with the Compose plugin.

Get the project
---------------

Clone your public GitHub repository and enter the project folder::

   git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
   cd YOUR_REPOSITORY_NAME

Replace the example GitHub username and repository name with your actual values.

Local setup (Windows PowerShell)
--------------------------------

Create and activate a virtual environment, then install dependencies::

   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt

On macOS/Linux, activate the environment with::

   source venv/bin/activate

Create a database named ``news_capstone`` in your MySQL/MariaDB server and
create a database user with permissions on that database. Set the environment
variables listed in ``.env.example`` in your terminal or local environment.
Use your own password and never commit it to GitHub.

Then run::

   python manage.py check
   python manage.py migrate
   python manage.py test
   python manage.py runserver

Open ``http://127.0.0.1:8000/`` in your browser.

Docker setup
------------

Docker instructions are independent of the local virtual-environment setup.
From the cloned project root, start the application and database together::

   docker compose up --build

The Compose configuration creates the ``news_capstone`` database and starts
the Django application after the database reports healthy. Open
``http://127.0.0.1:8000/``. To stop the services, press Ctrl+C and then run::

   docker compose down

To remove the local database volume as well (this permanently deletes its
stored data), run ``docker compose down -v``.

Build the Sphinx documentation
------------------------------

Install project dependencies, then run::

   python -m sphinx -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser.
