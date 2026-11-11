# Contributing to ArtifactX

Thank you for your interest in contributing to ArtifactX Community Edition.

## Development setup

See [README.md](./README.md#local-development-without-docker) for backend and frontend setup.

## Before submitting a change

1. Run the backend test suite: `cd backend && pytest -v`
2. Run the frontend build and tests: `cd frontend && npm run build && npm run test`
3. Lint the frontend: `npm run lint`
4. Keep changes scoped to one module where possible (see [ARCHITECTURE.md](./ARCHITECTURE.md)
   for the module boundaries)

## Database changes

Any model change must come with an Alembic migration:

```bash
cd backend
alembic revision --autogenerate -m "describe the change"
