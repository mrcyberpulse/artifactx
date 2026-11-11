# Security Policy

## Supported versions

ArtifactX Community Edition is in active initial development (v1.0.0, Part 1 of 4). Security
fixes are applied to the `main` branch only at this stage.

## Reporting a vulnerability

Please do **not** open a public issue for security vulnerabilities. Instead, report privately
to the maintainer:

- **Contact**: Harsh Saini — via the contact details on **Mail** manager.prachi@zohomail.in and cc cyber.h4rsh@zohomail.in
- Include: a description of the issue, reproduction steps, and the affected version/commit.

You should expect an initial acknowledgment within a reasonable timeframe. Coordinated
disclosure is requested: please allow time for a fix before public disclosure.

## Current security posture (Part 1)

Implemented:
- Argon2 password hashing (industry-standard, memory-hard)
- Short-lived JWT access tokens kept in frontend memory only (not `localStorage`)
- Refresh tokens as `HttpOnly`, `SameSite=Strict` cookies for browsers; stored server-side only
  as a keyed SHA-256 hash (never in plaintext)
- Refresh token rotation with reuse detection (compromise of one token revokes its whole family)
- Rate limiting on login, registration, and password reset endpoints
- Workspace isolation returning 404 (not 403) to non-members, preventing existence probing
- Structured error responses that never echo submitted credentials
- Security headers (CSP, X-Frame-Options, HSTS when `ARTIFACTX_COOKIE_SECURE=true`, etc.)

Not yet implemented (tracked for later parts):
- File upload scanning and sandboxing (Part 2 — SBOM files will be treated as untrusted input
  with strict size limits, safe XML parsing, and no execution of file contents)
- Outbound request restrictions for vulnerability intelligence sources (Part 3 — SSRF protections
  will apply when fetching from OSV/NVD/KEV/EPSS)

This document does not claim ArtifactX is free of vulnerabilities. Report anything you find.
