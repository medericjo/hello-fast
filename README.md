# hello-fast

A FastAPI service built with clean architecture. It serves posts and users
fetched from [JSONPlaceholder](https://jsonplaceholder.typicode.com).

> 📖 **Full walkthrough of every step:** [docs/STEP_BY_STEP.md](docs/STEP_BY_STEP.md)

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Endpoints

| Method | Path                            | Description                        |
|--------|---------------------------------|------------------------------------|
| GET    | `/health`                       | Liveness check                     |
| GET    | `/api/v1/posts`                 | All posts (`?user_id=` to filter)  |
| GET    | `/api/v1/posts/{post_id}`       | One post                           |
| GET    | `/api/v1/users`                 | All users                          |
| GET    | `/api/v1/users/{user_id}`       | One user                           |
| GET    | `/api/v1/users/{user_id}/posts` | Posts of a user                    |

## Layers

```
app/
├── domain/          entities, repository interfaces, exceptions (no frameworks)
├── application/     use cases
├── infrastructure/  httpx client + JSONPlaceholder repositories
├── presentation/    FastAPI routes, schemas, dependency injection
└── core/            settings
```

## Tests

```bash
pytest -v
```
