
# ArtifactX — Community Edition

**Open-source Software Bill of Materials (SBOM) intelligence platform for software supply-chain security.**

Created by **MR Cyber Pulse** (https://github.com/mrcyberpulse)) · Licensed under MIT.

> This is **Part 1 of 4** of the ArtifactX build. It establishes the architecture, backend, database, authentication, workspace/project management, and the full visual GUI foundation. SBOM parsing, vulnerability intelligence, risk scoring, reporting, and the CLI are **not yet implemented** — see [Roadmap](#roadmap).

## Features in this release

- User registration, login, logout, password reset (architecture), rate limiting
- JWT access tokens (in-memory on the frontend) + rotating refresh tokens with reuse detection
- Workspaces with role-based membership (owner/admin/member/viewer)
- Project CRUD with search, filter, and pagination
- Workspace-isolated audit logging
- Health check endpoint (DB + Redis)
- Dashboard with real project metrics; other metrics show honest "coming soon" states
- Full dark cybersecurity GUI with all 14 planned sidebar sections (9 are placeholders)

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, React Hook Form, Zod, Radix UI |
| Backend | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis |
| Desktop/Mobile | Tauri 2 (scaffolded, see `desktop/` and `mobile/`) |
| Deployment | Docker, Docker Compose |

## Local development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # edit ARTIFACTX_SECRET_KEY and ARTIFACTX_DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload --port 8000
