# FastAPI Calculator with Secure User Accounts

A FastAPI application with a calculator and secure user registration. Users are stored in PostgreSQL with SQLAlchemy, validated with Pydantic, and their passwords are hashed with bcrypt. Every push to `main` runs the tests in GitHub Actions against a real PostgreSQL database, scans the Docker image for vulnerabilities, and publishes it to Docker Hub.

**Docker Hub repository:** https://hub.docker.com/r/desaiveds/module10_is601

## Features

- **SQLAlchemy `User` model:** `id`, `username` (unique), `email` (unique), `password_hash` and `created_at`.
- **Pydantic schemas:**
  - `UserCreate`: `username`, `email` and `password`. It validates the email with `EmailStr`, requires 3-50 safe characters for the username, and requires a password of 8-64 characters with at least one letter and one digit.
  - `UserRead`: `id`, `username`, `email` and `created_at`. It never includes the password or its hash.
- **Password hashing:** `hash_password()` and `verify_password()` in `app/security.py` use bcrypt with a random salt. Only the hash is stored.
- **API:**
  - `POST /users/register`: creates a user (201), or returns 400 if the username or email is already taken, or 422 for invalid data.
  - `GET /users/{id}`: returns a user's public details.
  - `POST /add`, `/subtract`, `/multiply`, `/divide`: calculator operations.
  - `GET /`: the calculator web page. `GET /health`: health check.

## Running Tests Locally

1. Create a virtual environment and install the dependencies:
   ~~~bash
   python -m venv venv
   source venv/Scripts/activate     # Windows (Git Bash)
   # source venv/bin/activate       # macOS / Linux
   pip install -r requirements.txt
   ~~~

2. Start PostgreSQL. Integration tests need a real database, and the `db` service from Docker Compose provides one:
   ~~~bash
   docker compose up -d db
   ~~~

3. Run the tests:
   ~~~bash
   pytest tests/unit          # unit tests (no database needed)
   pytest tests/integration   # integration tests (PostgreSQL container)
   pytest --cov=app --cov=main --cov-report=term-missing   # everything, with coverage
   ~~~
   The tests connect using `DATABASE_URL`, which defaults to `postgresql://postgres:postgres@localhost:5432/fastapi_db`. To use a different database, copy `.env.example` to `.env` and edit it.

   > **Warning:** the integration tests empty the `users` table, so don't point `DATABASE_URL` at data you want to keep.

4. Stop the database when you're done: `docker compose down`

## Running the Application

**With Docker Compose (app + database + pgAdmin):**
~~~bash
docker compose up --build
~~~
- App: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (login `admin@example.com` / `admin`; database host `db`, user `postgres`, password `postgres`)

**From Docker Hub:**
~~~bash
docker pull desaiveds/module10_is601:latest
docker run -p 8000:8000 desaiveds/module10_is601:latest
~~~
The calculator works on its own. The user endpoints need a database, so pass one with `-e DATABASE_URL=postgresql://user:password@host:5432/dbname`.

## CI/CD Pipeline

`.github/workflows/ci-cd.yml` runs on every push and pull request to `main`:

1. **test:** starts a PostgreSQL 16 service container, runs the unit tests, then runs the integration tests against the real database. It fails if coverage drops below 90%.
2. **security:** builds the Docker image and scans it with Trivy. It fails on fixable HIGH or CRITICAL vulnerabilities.
3. **deploy:** runs only on pushes to `main`, after the first two jobs pass. It pushes the image to Docker Hub as `desaiveds/module10_is601:latest` and `desaiveds/module10_is601:<commit-sha>`.

The deploy job uses two repository secrets, set in **GitHub → Settings → Secrets and variables → Actions**: `DOCKERHUB_USERNAME` (the Docker Hub username) and `DOCKERHUB_TOKEN` (a Docker Hub access token with Read & Write permission).
