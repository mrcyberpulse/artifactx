# Changelog

All notable changes to ArtifactX are documented in this file.

## [1.0.0] - Part 1: Foundation — Unreleased

### Added
- FastAPI backend with modular packages: auth, users, workspaces, projects, dashboard, audit, health
- PostgreSQL schema via SQLAlchemy + Alembic (initial migration: users, workspaces, memberships, projects, refresh tokens, password reset tokens, audit events)
- JWT access tokens + rotating refresh tokens with reuse detection
- Registration, login, logout, password reset request/confirm flows
- Rate limiting on auth endpoints (Redis-backed, with in-process fallback)
- Workspace creation and membership with role-based access control (owner/admin/member/viewer)
- Project CRUD with search, filtering, and pagination
- Workspace-isolated audit event logging
- Health check endpoint covering database and Redis connectivity
- React + TypeScript + Vite frontend with Tailwind dark cybersecurity design system
- Full sidebar navigation for all 14 planned modules (5 functional, 9 marked "coming soon")
- Dashboard with real project count and honest empty states for unimplemented metrics
- Docker Compose deployment (frontend, backend, PostgreSQL, Redis) with health checks
- Backend pytest suite covering auth, workspace isolation, and project lifecycle
- Tauri desktop/mobile scaffolding with documented build requirements

### Known limitations
- SBOM import, vulnerability scanning, risk scoring, license analysis, remediation, reporting, notifications, and the dependency graph are not implemented — placeholders only (Parts 2–4)
- Password reset emails are logged server-side in development, not actually delivered (no SMTP transport configured)
- No workspace member invitation UI yet (membership currently only created implicitly for the workspace owner)
