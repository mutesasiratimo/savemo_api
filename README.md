## Save Mo Finance Backend (FastAPI)

This is the FastAPI backend for **Save Mo Finance**, a savings and loans management platform driven by the feature specification in `Features.MD`.

### Stack

- FastAPI
- PostgreSQL
- SQLAlchemy 2.x with Alembic migrations
- Pydantic for request/response schemas
- Docker + Docker Compose for local development

### Running the app

**With Docker (recommended)**

From the project root:

```bash
docker compose up --build
```

- Postgres starts first; the API waits for it to be healthy, then runs `alembic upgrade head` and starts uvicorn.
- API: **http://localhost:8000**
- Interactive docs: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

**Without Docker**

1. Create a PostgreSQL database and set its URL:

   ```bash
   export DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/savemo
   ```

2. Create a virtualenv, install deps, run migrations, then start the server:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or: .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload --port 8000
   ```

   API and docs URLs are the same as above.

### Default admin (after migrations)

- **Email:** `admin@email.com`
- **Password:** `admin123`

The seed migration creates an **admin** role with ACL `all` and assigns it to this user. Use roles (and the `all` permission) instead of the legacy `is_superuser` flag.

### CI: GHCR image

On every push to `main`, GitHub Actions builds the API image and pushes it to [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry):

- **Image:** `ghcr.io/<owner>/<repo>:latest` and `ghcr.io/<owner>/<repo>:<sha>`
- Workflow: `.github/workflows/build-push-ghcr.yml`
- No secrets required; `GITHUB_TOKEN` is used to push. For private repos, the image is private by default.

To run the published image (after setting `DATABASE_URL`):

```bash
docker run --rm -e DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db ghcr.io/<owner>/<repo>:latest
```

### Auth

- **Login** (`POST /api/v1/auth/login`) returns both `access_token` and `refresh_token`.
- **Refresh** (`POST /api/v1/auth/refresh`) body: `{ "refresh_token": "..." }` returns a new access and refresh token pair.

### Project Structure (high-level)

- `app/main.py` – FastAPI app factory and startup configuration.
- `app/core/` – settings, security, and common config.
- `app/db/` – database session, base models, and migrations hooks.
- `app/models/` – SQLAlchemy models (users, groups, goals, wallets, loans, events, notifications, finance, etc.).
- `app/schemas/` – Pydantic models for API I/O.
- `app/api/` – Routers grouped by domain (auth, groups, goals, wallets, loans, events, notifications, finance).
- `app/services/` – Domain/business logic services.
- `app/background/` – Background tasks for reminders, notifications, and async processing.

See `Features.MD` for the full product/feature requirements.

