# Building hello-fast, step by step

This guide records every step taken to create this project, in order, with the
reason behind each one. You can follow it to rebuild the project from an empty
folder.

---

## Step 0: Check the tools you have

```bash
python3 --version     # Python 3.9.6 on this machine (macOS system Python)
```

FastAPI needs Python 3.8 or newer, so 3.9 works. Because 3.9 is old, the code
uses `typing.List` / `typing.Optional` instead of the newer `list[int]` /
`int | None` syntax. If you install a newer Python later (for example with
`brew install python@3.12`), the code still works unchanged.

---

## Step 1: Create a virtual environment

```bash
cd /Users/macos/devs/iat/hello-fast
python3 -m venv .venv
source .venv/bin/activate        # your prompt now shows (.venv)
pip install --upgrade pip
```

**Why:** a virtual environment (`.venv/`) keeps this project's packages
separate from your system Python and from your other projects.

Run `deactivate` to leave it. Each time you open a new terminal, run
`source .venv/bin/activate` again.

---

## Step 2: Install the dependencies

```bash
pip install fastapi "uvicorn[standard]" httpx pydantic-settings pytest pytest-asyncio
```

| Package             | Role                                                         |
|---------------------|--------------------------------------------------------------|
| `fastapi`           | The web framework (routing, validation, OpenAPI docs)        |
| `uvicorn[standard]` | The ASGI server that runs the app                            |
| `httpx`             | Async HTTP client used to call JSONPlaceholder               |
| `pydantic-settings` | Reads configuration from environment variables and `.env`    |
| `pytest`            | Test runner                                                  |
| `pytest-asyncio`    | Lets pytest run `async def` tests                            |

The exact versions are pinned in two files:

- `requirements.txt`: what the app needs at runtime
- `requirements-dev.txt`: runtime plus test tools (it includes `-r requirements.txt`)

On a fresh clone, run: `pip install -r requirements-dev.txt`

---

## Step 3: Understand clean architecture before writing code

Clean architecture splits code into layers. The rule is that **dependencies
point inward only**: outer layers may import inner layers, never the other way
round.

```
 ┌──────────────────────────────────────────────────────┐
 │ presentation   (FastAPI routes, schemas, DI wiring)  │
 │  ┌────────────────────────────────────────────────┐  │
 │  │ infrastructure (httpx, JSONPlaceholder adapters)│  │
 │  │  ┌──────────────────────────────────────────┐  │  │
 │  │  │ application   (use cases)                │  │  │
 │  │  │  ┌────────────────────────────────────┐  │  │  │
 │  │  │  │ domain (entities, repository       │  │  │  │
 │  │  │  │         interfaces, exceptions)    │  │  │  │
 │  │  │  └────────────────────────────────────┘  │  │  │
 │  │  └──────────────────────────────────────────┘  │  │
 │  └────────────────────────────────────────────────┘  │
 └──────────────────────────────────────────────────────┘
```

| Layer            | Knows about FastAPI? | Knows about HTTP/httpx? | Purpose                              |
|------------------|:--------------------:|:-----------------------:|--------------------------------------|
| `domain`         | no                   | no                      | Business objects and rules           |
| `application`    | no                   | no                      | Use cases: "what the app does"       |
| `infrastructure` | no                   | yes                     | Talks to the outside world           |
| `presentation`   | yes                  | no (only via DI)        | Turns HTTP requests into use cases   |

**What this buys you:** to replace JSONPlaceholder with a real database, you
write one new repository class in `infrastructure/` and change one line in
`dependencies.py`. The domain, the use cases and the routes stay the same.

---

## Step 4: Create the folder structure

```bash
mkdir -p app/core app/domain/entities app/domain/repositories \
         app/application/use_cases \
         app/infrastructure/http app/infrastructure/repositories \
         app/presentation/api/v1/routes app/presentation/schemas \
         tests docs
# Every package folder needs an __init__.py so Python can import it
find app tests -type d -exec touch {}/__init__.py \;
```

Result:

```
hello-fast/
├── app/
│   ├── main.py                         # composition root: builds the FastAPI app
│   ├── core/config.py                  # settings (.env)
│   ├── domain/
│   │   ├── entities/post.py, user.py   # pure dataclasses
│   │   ├── repositories/               # abstract interfaces ("ports")
│   │   └── exceptions.py               # NotFoundError, ExternalServiceError
│   ├── application/use_cases/          # ListPosts, GetPost, ListUsers, ...
│   ├── infrastructure/
│   │   ├── http/jsonplaceholder_client.py
│   │   └── repositories/               # JSONPlaceholder implementations ("adapters")
│   └── presentation/
│       ├── schemas/                    # Pydantic response models
│       └── api/
│           ├── dependencies.py         # dependency injection wiring
│           ├── error_handlers.py       # domain errors → HTTP status codes
│           └── v1/router.py, routes/   # endpoints
├── tests/
├── docs/STEP_BY_STEP.md                # this file
├── .env / .env.example
├── requirements.txt / requirements-dev.txt
└── pytest.ini
```

---

## Step 5: Configuration (`app/core/config.py`, `.env`)

`Settings` is a `pydantic_settings.BaseSettings` class. Each field is read from
an environment variable with the same name (case-insensitive), or from `.env`
if the variable is not set, or falls back to the default value.

```
APP_NAME=hello-fast
JSONPLACEHOLDER_BASE_URL=https://jsonplaceholder.typicode.com
HTTP_TIMEOUT_SECONDS=10
```

- `.env.example` is committed so others know which variables exist.
- `.env` holds your local values and is git-ignored, so secrets never get committed.
- `get_settings()` uses `@lru_cache`, so the file is read only once.

---

## Step 6: The domain layer (the core)

**Entities** (`app/domain/entities/post.py`, `user.py`) are plain frozen
dataclasses. They use Python naming (`user_id`), not the API's naming
(`userId`). The domain describes *your* model, not JSONPlaceholder's.

**Repository interfaces** (`app/domain/repositories/*.py`) are abstract classes
(`ABC`) that say *what* data operations exist, not *how* they work:

```python
class PostRepository(ABC):
    async def list(self, user_id: Optional[int] = None) -> List[Post]: ...
    async def get(self, post_id: int) -> Optional[Post]: ...
```

**Exceptions** (`app/domain/exceptions.py`): `NotFoundError` and
`ExternalServiceError`. The domain raises these. It never raises
`HTTPException`, because the domain does not know about HTTP.

---

## Step 7: The application layer (use cases)

Each use case is a small class with one `execute()` method
(`app/application/use_cases/posts.py`, `users.py`):

| Use case        | What it does                                                 |
|-----------------|--------------------------------------------------------------|
| `ListPosts`     | All posts, optionally filtered by author                     |
| `GetPost`       | One post; raises `NotFoundError` if missing                  |
| `ListUsers`     | All users                                                    |
| `GetUser`       | One user; raises `NotFoundError` if missing                  |
| `ListUserPosts` | Checks that the user exists, then returns their posts. This one combines two repositories. |

Use cases receive repositories in their constructor, typed as the *interface*.
This is **dependency inversion**: the use case does not know or care whether
the data comes from JSONPlaceholder, a database, or a test fake.

---

## Step 8: The infrastructure layer (getting data from JSONPlaceholder)

JSONPlaceholder (https://jsonplaceholder.typicode.com) is a free fake REST API.
The endpoints used here:

| Upstream request          | Returns                    |
|---------------------------|----------------------------|
| `GET /posts`              | 100 posts                  |
| `GET /posts?userId=1`     | posts written by user 1    |
| `GET /posts/1`            | one post (404 if missing)  |
| `GET /users`              | 10 users                   |
| `GET /users/1`            | one user (404 if missing)  |

**`JsonPlaceholderClient`** (`app/infrastructure/http/jsonplaceholder_client.py`)
wraps `httpx.AsyncClient`:

- returns parsed JSON on success
- returns `None` on 404, so the caller decides that this means "not found"
- raises `ExternalServiceError` on network errors or 5xx responses

**Repositories** (`app/infrastructure/repositories/*.py`) implement the domain
interfaces. Their main job is **mapping**: they turn the raw JSON
(`{"userId": 1, ...}`) into domain entities (`Post(user_id=1, ...)`).
JSONPlaceholder returns extra user fields (`address`, `company`); the mapper
keeps only the fields the domain needs.

---

## Step 9: The presentation layer (FastAPI)

**Schemas** (`app/presentation/schemas/`): Pydantic models (`PostOut`,
`UserOut`) that define the public JSON shape. `from_attributes=True` lets
FastAPI build them directly from the domain dataclasses.

**Dependency injection** (`app/presentation/api/dependencies.py`): this is the
only file that knows which concrete class implements each interface:

```
Request → get_client → get_post_repository → get_list_posts → route
          (httpx)      (JsonPlaceholder...)   (ListPosts)
```

FastAPI's `Depends()` resolves this chain on every request.

**Routes** (`app/presentation/api/v1/routes/`): these are thin. Each one calls a
use case and returns the result.

**Error handlers** (`app/presentation/api/error_handlers.py`) translate domain
exceptions into HTTP status codes:

| Domain exception        | HTTP status          |
|-------------------------|----------------------|
| `NotFoundError`         | 404 Not Found        |
| `ExternalServiceError`  | 502 Bad Gateway      |

---

## Step 10: Assemble the app (`app/main.py`)

`create_app()` builds the FastAPI instance, registers the error handlers,
mounts `/api/v1` and adds `/health`.

The `lifespan` function creates **one** shared `httpx.AsyncClient` at startup
and closes it at shutdown. Reusing a single client keeps connections pooled,
which is much faster than opening a new connection on every request.

---

## Step 11: Run it

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

`--reload` restarts the server whenever you save a file. Then open:

- Swagger UI (interactive docs): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Endpoints:

| Method | Path                          | Description                    |
|--------|-------------------------------|--------------------------------|
| GET    | `/health`                     | Liveness check                 |
| GET    | `/api/v1/posts`               | All posts (`?user_id=1` to filter) |
| GET    | `/api/v1/posts/{post_id}`     | One post                       |
| GET    | `/api/v1/users`               | All users                      |
| GET    | `/api/v1/users/{user_id}`     | One user                       |
| GET    | `/api/v1/users/{user_id}/posts` | Posts of a user              |

Try it:

```bash
curl http://127.0.0.1:8000/api/v1/posts/1
curl "http://127.0.0.1:8000/api/v1/posts?user_id=2"
curl http://127.0.0.1:8000/api/v1/users/1/posts
curl -i http://127.0.0.1:8000/api/v1/users/999     # → 404
```

Verified output during setup (against live JSONPlaceholder):

```
GET /health                 → {"status":"ok"}
GET /api/v1/posts/1         → {"id":1,"user_id":1,"title":"sunt aut facere ...", ...}
GET /api/v1/posts?user_id=2 → 10 posts
GET /api/v1/users/1         → {"id":1,"name":"Leanne Graham","username":"Bret", ...}
GET /api/v1/users/1/posts   → 10 posts
GET /api/v1/users/999       → 404 {"detail":"User with id=999 not found"}
```

---

## Step 12: Tests

```bash
pytest -v
```

`pytest.ini` sets `asyncio_mode = auto`, so `async def test_...` functions run
without needing a decorator. Each layer is tested in isolation, and **no test
calls the real internet**:

| File                                    | Tests                    | How                                               |
|-----------------------------------------|--------------------------|---------------------------------------------------|
| `tests/test_use_cases.py`               | application layer        | In-memory fake repositories (`tests/fakes.py`)    |
| `tests/test_jsonplaceholder_repository.py` | infrastructure layer  | `httpx.MockTransport` returns canned responses    |
| `tests/test_api.py`                     | presentation layer       | `TestClient` + `app.dependency_overrides` swaps in the fakes |

Result during setup: **9 passed**.

The fakes are only possible because the use cases depend on interfaces. This
is clean architecture paying off in practice.

---

## Step 13: Extending the project (example: comments)

To add `GET /api/v1/posts/{id}/comments`, touch each layer from the inside out:

1. `domain/entities/comment.py`: add a `Comment` dataclass
2. `domain/repositories/comment_repository.py`: add a `CommentRepository(ABC)` with `list_by_post(post_id)`
3. `application/use_cases/comments.py`: add `ListPostComments`, which checks that the post exists, then lists its comments
4. `infrastructure/repositories/jsonplaceholder_comment_repository.py`: call `GET /posts/{id}/comments` and map `postId` to `post_id`
5. `presentation/schemas/comment.py`: add `CommentOut`
6. `presentation/api/dependencies.py`: add providers for the new repository and use case
7. `presentation/api/v1/routes/posts.py`: add the route
8. `tests/`: add a fake and tests
