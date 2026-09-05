# SmartVitra instructions for coding agents

## Scope and safety

- Work from this repository root and preserve pre-existing user changes.
- Never print, commit, or place credentials from `.env` in commands or logs.
- Inspect before editing; use `apply_patch` for hand-written changes.
- Do not deploy until backend tests, type checking, and frontend build pass.

## Token-efficient discovery

- Start architecture/code-flow questions with Graphify MCP: `graph_stats`, then a focused `query_graph` using depth 1-2 and a token budget of 800-1600.
- If MCP is unavailable, use `graphify query "<specific question>" --graph graphify-out/graph.json --budget 1200`.
- Refresh the graph only after structural changes: `graphify extract . --code-only --out .`.
- Follow graph results with narrow `rg` searches and small line ranges. Do not dump whole directories, generated files, fixtures, backups, or lockfiles unless the task needs them.
- Keep one task focused on one outcome; summarize established facts instead of reopening the same files.

## Architecture and commands

- Read `ARCHITECTURE.md` and `PROJECT_OVERVIEW.md` first.
- Backend: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, Alembic.
- Frontend: React, TypeScript, Vite.
- Production: one Docker image deployed to `smartvitra-web` and `smartvitra-generation` in `europe-west3`.
- Validate with `black backend tests`, `ruff check backend tests`, `mypy backend`, `pytest`, and `npm run build` in `frontend`.

## Definition of done

- The requested behavior has focused regression coverage.
- Full validation passes or any unrelated pre-existing failure is clearly identified.
- Frontend is rebuilt if changed.
- Production work includes a unique image tag, synchronized web/job images, health verification, and a real user-level test.
