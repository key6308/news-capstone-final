Troubleshooting
===============

Database connection errors
--------------------------

Messages such as ``Can't connect to MySQL server`` or ``Access denied for
user`` mean Django cannot reach the database. Check that:

* MySQL/MariaDB is running.
* The ``news_capstone`` database exists.
* ``DB_NAME``, ``DB_USER``, ``DB_PASSWORD``, ``DB_HOST``, and ``DB_PORT`` are
  set in ``.env`` or in the terminal you run Django from, and match the
  database.

If ``python manage.py test`` reports ``Access denied`` for
``test_news_capstone``, grant the database user rights to the test database
(see :doc:`installation`). If PyMySQL reports that the ``cryptography``
package is required, you are using MySQL 8: run
``python -m pip install cryptography``.

With Docker Compose, the database host is the service name ``db``, not
``127.0.0.1``. Compose sets this for you.

Missing Python packages
-----------------------

``ModuleNotFoundError`` usually means the virtual environment is not active
or the requirements are not installed:

.. code-block:: powershell

   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt

PowerShell will not run a script
--------------------------------

If PowerShell reports that running scripts is disabled, allow scripts for the
current terminal only:

.. code-block:: powershell

   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Or run a single script without changing the policy:

.. code-block:: powershell

   powershell -ExecutionPolicy Bypass -File .\build_docs.ps1

``py`` is not recognized
------------------------

The ``py`` launcher is only installed by the python.org installer. Use
``python`` instead, and check the version with ``python --version``.

Migration errors
----------------

Run ``python manage.py migrate`` again after confirming the database is
reachable.

Approval says "API logging failed"
----------------------------------

When an editor approves an article, the app calls ``APPROVED_API_URL``. The
article is still approved if that call fails. Check that the URL points to the
running server, for example ``http://127.0.0.1:8000/api/approved/``, and
that the server's address and port match the ones you started it on.

Documentation build problems
----------------------------

See :doc:`building_docs`.
