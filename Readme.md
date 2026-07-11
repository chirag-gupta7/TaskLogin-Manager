# TaskFlow API

A Task Management REST API built with **FastAPI**, featuring JWT authentication, password hashing, and role-based access control (RBAC). Users can create and manage their own tasks; admins can manage any task.

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite (via SQLAlchemy ORM)
- **Auth:** JWT access tokens (`python-jose`), password hashing with `passlib[bcrypt]`
- **Validation:** Pydantic v2
- **Testing:** Pytest + FastAPI's `TestClient` (httpx)

## Features

- User registration and login
- Passwords hashed with bcrypt — never stored in plain text
- JWT-based authentication on protected routes
- Task CRUD (Create, Read, Update, Delete)
- Task ownership — users can only modify their own tasks
- Role-Based Access Control — admins can bypass ownership restrictions
- Centralized error handling (clean 4xx/5xx responses, no leaked stack traces)
- Automated test suite covering auth and task ownership logic

## Project Structure

```
.
├── main.py         # FastAPI app, routes, auth dependency, exception handlers
├── models.py       # SQLAlchemy models (User, Task)
├── schema.py       # Pydantic schemas (request/response validation)
├── security.py     # Password hashing + JWT creation
├── database.py     # SQLAlchemy engine/session setup
├── test_main.py    # Pytest test suite
└── tasklogin.db    # SQLite database file (created automatically)
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tasklogin-manager
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn sqlalchemy "passlib[bcrypt]" "bcrypt==4.0.1" "python-jose[cryptography]" "pydantic[email]" pytest httpx
   ```

4. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open the interactive API docs**

   Visit `http://127.0.0.1:8000/docs` (Swagger UI).

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | `/health` | No | Health check |
| POST | `/api/v1/auth/register` | No | Register a new user |
| POST | `/api/v1/auth/login` | No | Log in, returns a JWT access token |
| GET | `/api/v1/users/me` | Yes | Get the currently logged-in user's profile |
| POST | `/api/v1/tasks` | Yes | Create a new task (owned by the current user) |
| GET | `/api/v1/tasks` | Yes | List all tasks owned by the current user |
| GET | `/api/v1/tasks/{id}` | No* | Get a single task by ID |
| PUT | `/api/v1/tasks/{id}` | Yes | Update a task (owner or admin only) |
| DELETE | `/api/v1/tasks/{id}` | Yes | Delete a task (owner or admin only) |

\* `GET /api/v1/tasks/{id}` is not yet protected by authentication or ownership checks — this is a known gap, not an intentional public endpoint. See **Known Limitations** below.

### Authentication flow

1. Register via `POST /api/v1/auth/register`.
2. Log in via `POST /api/v1/auth/login` with `username` and `password` — response includes an `access_token`.
3. For protected routes, send the token as a header:
   ```
   Authorization: Bearer <access_token>
   ```
   In Swagger UI, click **Authorize** and paste the raw token.

### Roles

- New users default to role `"user"`.
- `"admin"` role users can update/delete any task, not just their own.
- There is no API endpoint to self-promote to admin (by design). Role changes must currently be done manually at the database level — see `make_admin.py` for an example script.

## Running Tests

```bash
pytest -v
```

Tests run against a separate SQLite file (`test.db`), fully isolated from `tasklogin.db`. The test database is wiped and recreated before every test run via an `autouse` pytest fixture, so tests do not depend on each other or on leftover data.

Current coverage includes:
- User registration (success + duplicate username rejection)
- Login (success + wrong password)
- Auth enforcement on protected routes
- Task creation
- Task list isolation (users only see their own tasks)
- Ownership enforcement on updates (a user cannot edit another user's task)

## Known Limitations / TODO

- **`SECRET_KEY` is hardcoded** in `security.py` for development convenience. Before any real deployment, this must be moved to an environment variable and replaced with a properly generated random secret.
- **`GET /api/v1/tasks/{id}` has no auth or ownership check** — currently anyone can fetch any task by ID. Needs the same `Depends(get_current_user)` + ownership check pattern used in the update/delete endpoints.
- No pagination or filtering on `GET /api/v1/tasks`.
- No refresh tokens — access tokens expire after 30 minutes and require re-login.
- No Docker setup yet.
- Uses SQLite for both dev and testing; production use would call for PostgreSQL.

## Roadmap

- [Done] Fix unprotected `GET /api/v1/tasks/{id}`
- [ ] Move `SECRET_KEY` to environment variable (`.env` + `python-dotenv`)
- [ ] Dockerfile + docker-compose
- [ ] Pagination/filtering on task list
- [ ] Refresh tokens