# Django News Application — Capstone Consolidation

This project is a Django news application with reader, journalist, and editor roles. It supports article submission and approval, newsletters, subscriptions, email notifications, and a token-authenticated Django REST Framework API.

## Documentation

**The Sphinx documentation is pre-built and committed. Open [`docs/_build/html/index.html`](docs/_build/html/index.html) in a web browser. You don't need to install or build anything.**

It covers installation, a quickstart walkthrough, the REST API endpoints, troubleshooting, and a full API reference generated from the code's docstrings.

## Project structure

- `manage.py` — Django command-line entry point.
- `news_application/` — Django settings and top-level URLs.
- `news/` — models, forms, views, API endpoints, tests, templates, and static files.
- `Planning/` — system requirements, API design, UI/UX, data model, and test planning.
- `docs/` — Sphinx source (`conf.py`, `index.rst`, pages, `api/`, `_static/`, `_templates/`, `Makefile`, `make.bat`) and the rendered HTML in `docs/_build/html/`.
- `build_docs.ps1` — one-step documentation rebuild for Windows PowerShell (wraps `docs/build_docs.ps1`).
- `Dockerfile` and `compose.yaml` — container build and Django + MariaDB services.
- `requirements.txt` — pinned Python dependencies, including Sphinx and its theme.
- `.env.example` — template for the environment variables (copy it to `.env`).
- `.flake8` — PEP 8 checker settings. Run `python -m pip install flake8`, then `flake8` from the project root.

## Option A: Run locally with a virtual environment

You need Python 3.12 and a running database server. MariaDB is recommended. MySQL 8 also works, but see the note in step 2.

### 1. Get the code

```bash
git clone https://github.com/key6308/news-capstone-consolidation.git
cd news-capstone-consolidation
```

### 2. Create and activate a virtual environment

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If the `py` launcher isn't installed, use `python -m venv .venv` instead. If PowerShell blocks activation, allow scripts for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**MySQL 8 only:** MySQL 8 uses `caching_sha2_password` authentication, which the PyMySQL driver can only handle when the `cryptography` package is installed. Run `python -m pip install cryptography` in the activated environment. MariaDB doesn't need it.

### 3. Create the database and user

Open the database client as an administrator (`mariadb -u root -p` or `mysql -u root -p`) and run the following SQL. Replace `choose-a-password` with your own password.

```sql
CREATE DATABASE news_capstone CHARACTER SET utf8mb4;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'choose-a-password';
GRANT ALL PRIVILEGES ON news_capstone.* TO 'news_user'@'localhost';
GRANT ALL PRIVILEGES ON `test_news_capstone`.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
```

The second `GRANT` is needed because `python manage.py test` creates and deletes a temporary `test_news_capstone` database.

### 4. Configure environment variables

`news_application/settings.py` reads its configuration from environment variables. `.env.example` lists all of them: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `APPROVED_API_URL`.

First generate a secret key (with the virtual environment active):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then choose **one** of these ways to set the variables.

**a) Use a `.env` file (recommended).** Copy the example file:

```powershell
Copy-Item .env.example .env      # Windows PowerShell
```

```bash
cp .env.example .env             # macOS / Linux
```

Open `.env` in an editor. Set `DJANGO_SECRET_KEY` to the key you generated and `DB_PASSWORD` to the password from step 3. Change the other values only if your database uses a different name, user, host, or port. `settings.py` loads `.env` from the project root automatically with `python-dotenv`, which is in `requirements.txt`. Git ignores `.env`, so your values stay on your computer.

**b) Set the variables in the terminal.** They last until you close the terminal, and they override values in `.env`.

Windows PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "paste-the-generated-key-here"
$env:DB_NAME = "news_capstone"
$env:DB_USER = "news_user"
$env:DB_PASSWORD = "choose-a-password"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3306"
```

macOS / Linux:

```bash
export DJANGO_SECRET_KEY="paste-the-generated-key-here"
export DB_NAME="news_capstone"
export DB_USER="news_user"
export DB_PASSWORD="choose-a-password"
export DB_HOST="127.0.0.1"
export DB_PORT="3306"
```

Never commit real passwords or secret keys.

### 5. Migrate, test, and run

With the virtual environment active and the database server running:

```bash
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. To try every role quickly, run `python manage.py seed_demo` to create demo accounts (see the Quickstart page in the documentation).

The public **Register** page creates reader and journalist accounts only. To create an editor, run `python manage.py createsuperuser`, sign in at `http://127.0.0.1:8000/admin/`, and set the user's **Role** to *Editor*.

## Option B: Run with Docker

Install Docker Desktop and make sure it is running. Docker Compose starts the Django web service and MariaDB database together. From the project root:

```powershell
docker compose up --build
```

When the containers are ready, open `http://127.0.0.1:8000/`. Stop the services with `Ctrl+C`, then run `docker compose down`. To delete the development database data too, run `docker compose down -v`.

Compose uses local-development fallback values for convenience. Before using this outside a local learning environment, set your own `DB_PASSWORD`, `DB_ROOT_PASSWORD`, and `DJANGO_SECRET_KEY` values. Never publish credentials in GitHub.

## Rebuilding the documentation (optional)

You only need this after changing the `.rst` pages or the docstrings. From the project root in PowerShell:

```powershell
.\build_docs.ps1
```

The script finds Python 3.12, creates `.venv` and installs `requirements.txt` if needed, then runs Sphinx with warnings treated as errors and writes the site to `docs/_build/html/`. No database is required. Add `-Clean` to delete the previous output first. If PowerShell blocks the script, run `powershell -ExecutionPolicy Bypass -File .\build_docs.ps1`.

On macOS/Linux, run `sh docs/build_docs.sh`. To build manually with the virtual environment active:

```powershell
python -m sphinx -W --keep-going -b html -d docs/_build/doctrees docs docs/_build/html
```

Commit `docs/_build/html/` after rebuilding so the published HTML stays current.

## API and demo data

API endpoints use token authentication where configured. Request a token through the project's token endpoint and send it using the header `Authorization: Token YOUR_TOKEN`. Keep tokens private. The `seed_demo` management command can create sample data for local testing; use only its local demo credentials and never deploy them.

## Git branch workflow

The repository includes `main`, `docs`, and `container` branches. Documentation source and per-script docstring commits are on `docs`; Docker configuration is on `container`; both branches have been merged into `main`. Verify with:

```powershell
git branch -a
git log --graph --oneline --decorate --all
git status
```
