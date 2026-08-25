# FlyRank BE-03 — Containerizing the stack with Postgres

A task CRUD API built with FastAPI, now running against a real PostgreSQL
database in Docker instead of SQLite. The API's endpoints, request bodies,
and responses are unchanged from the SQLite version (BE-02) — only the
storage layer moved from a local file to a containerized database server.

## Why Postgres in Docker

SQLite was a single file — simple, but not how real backends run in
production. Postgres is a proper database server, the same kind that
powers most real companies. Instead of installing Postgres directly on
this machine, it runs inside a Docker container: a throwaway, reproducible
environment that behaves identically on any machine.

## How to run this project

One command starts the whole stack — the API and the database together:

```bash
git clone https://github.com/barak-hub/flyrank-be02.git
cd flyrank-be02
cp .env.example .env
docker compose up
```

The API will be running at `http://localhost:8000`.

## Environment variables

Copy `.env.example` to `.env` before running by hand outside Docker.
Inside `docker compose`, the `DATABASE_URL` is set directly in
`compose.yaml` and points at the `db` service rather than `localhost`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get one task |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

## Example request

```bash
curl -i http://localhost:8000/tasks
```

```
HTTP/1.1 200 OK
content-type: application/json

[{"id":1,"title":"Buy groceries","done":false},{"id":2,"title":"Walk the dog","done":false},{"id":3,"title":"Write README","done":false}]
```

## Exploring the database directly

With the stack running, connect to Postgres via psql inside the container:

```bash
docker exec -it flyrank-be02-db-1 psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

![tasks table in psql](db-screenshot.png)

## What changed vs. BE-02

- The API's routes, request bodies, and response shapes are identical to
  the SQLite version.
- Only the storage layer changed: SQLite became Postgres, accessed via
  `psycopg` instead of the built-in `sqlite3` module.
- All queries use `%s` placeholders (psycopg's parameter style) instead
  of string formatting, to avoid SQL injection.
- `INSERT` now uses `RETURNING id` to get the new row's ID, replacing
  SQLite's `cur.lastrowid`.
- The whole stack — app and database — now starts with a single
  `docker compose up`, instead of running Python and a local file by hand.
