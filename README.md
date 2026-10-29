# Django News Application — Capstone Consolidation

This project is a Django news application with reader, journalist, and editor roles. It supports article submission and approval, newsletters, subscriptions, email notifications, and a token-authenticated Django REST Framework API.

## Project structure

- `manage.py` — Django command-line entry point.
- `news_application/` — Django settings and top-level URLs.
- `news/` — models, forms, views, API endpoints, tests, templates, and static files.
- `Planning/` — system requirements, API design, UI/UX, data model, and test planning.
- `docs/` — Sphinx source files and build scripts.
- `Dockerfile` and `compose.yaml` — container build and Django + MariaDB services.
- `requirements.txt` — pinned Python dependencies.

## Option A: Run locally on Windows

Install Python 3.12 and MySQL or MariaDB. From PowerShell, open the project root and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

Create a MariaDB/MySQL database named `news_capstone` and a database user with permissions for that database. Set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` in your terminal environment to match your own database. `news_application/settings.py` reads these variables. Do not commit real passwords or secret keys.

Then run:

```powershell
py manage.py check
py manage.py migrate
py manage.py test
py manage.py runserver
```

Open `http://127.0.0.1:8000/`. The local run commands require the database service to be running.

If PowerShell blocks activation, run this only in the current terminal and then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Option B: Run with Docker

Install Docker Desktop and make sure it is running. Docker Compose starts the Django web service and MariaDB database together. From the project root:

```powershell
docker compose up --build
```

When the containers are ready, open `http://127.0.0.1:8000/`. Stop the services with `Ctrl+C`, then run `docker compose down`. To delete the development database data too, run `docker compose down -v`.

Compose uses local-development fallback values for convenience. Before using this outside a local learning environment, set your own `DB_PASSWORD`, `DB_ROOT_PASSWORD`, and `DJANGO_SECRET_KEY` values. Never publish credentials in GitHub.

## Build the Sphinx documentation

Install the packages in `requirements.txt` in the active virtual environment. From the project root, run either:

```powershell
py -m sphinx -b html docs docs/_build/html
```

or run the PowerShell helper:

```powershell
.\docs\build_docs.ps1
```

After a successful build, open `docs/_build/html/index.html`. The HTML output is generated locally by Sphinx; commit `docs/_build/html/` after building so the generated documentation is available to the reviewer. The source documentation and `conf.py` are already in `docs/`.

## API and demo data

API endpoints use token authentication where configured. Request a token through the project's token endpoint and send it using the header `Authorization: Token YOUR_TOKEN`. Keep tokens private. The `seed_demo` management command can create sample data for local testing; use only its local demo credentials and never deploy them.

## Git branch workflow

The repository includes `main`, `docs`, and `container` branches. Documentation source and per-script docstring commits are on `docs`; Docker configuration is on `container`; both branches have been merged into `main`. Verify with:

```powershell
git branch -a
git log --graph --oneline --decorate --all
git status
```

## Submission

The HyperionDev task submission folder should contain only `capstone.txt`. That file should link to the public GitHub repository. The full application belongs in this repository, not as a ZIP attached to the assignment.
