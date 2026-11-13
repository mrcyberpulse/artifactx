#  ArtifactX — Community Edition

**An open-source, enterprise-grade Software Bill of Materials (SBOM) Intelligence Platform for software supply-chain security.**

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-cyan.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)

Created by **MR Cyber Pulse** (Harsh Saini). 

ArtifactX allows security teams and developers to upload SBOMs, detect vulnerable dependencies, calculate risk scores, and track remediation efforts — all within a premium dark-themed GUI.

##  Features (v1.0.0 Community Edition)

###  Authentication & Workspaces
- Secure JWT-based authentication (Argon2 password hashing).
- Multi-tenant Workspaces with Role-Based Access Control (Owner/Admin/Member/Viewer).
- Project management with search, filtering, and soft deletion.

###  SBOM Ingestion & Component Inventory
- **Formats Supported:** CycloneDX (JSON, XML) and SPDX (JSON, Tag-Value).
- Auto-detection of SBOM format.
- Extracts deep component data (PURL, Ecosystem, Licenses, Hashes, Dependencies).
- Full Component Inventory with search and filtering.

###  Vulnerability Intelligence & Risk Engine
- **Real OSV.dev API Integration** for fetching live vulnerabilities.
- Explainable Risk Scoring (0-100) based on CVSS, KEV status, and dependency type.
- Detailed finding tracking (Open, In Progress, Resolved).
- **License Intelligence:** Analyze license distribution and detect policy conflicts.
- **Dependency Graph:** Visualize component relationships.

###  Remediation & Reporting
- Create, assign, and track Remediation Tasks linked to specific vulnerabilities.
- Export professional **PDF** security reports and raw **CSV** data.
- Complete workspace Audit Logs.

##  Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, TanStack Query, React Hook Form, Zod |
| **Backend** | Python 3.11+, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL (Production) / SQLite (Testing) |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **CLI** | Standalone Python CLI (`artifactx_cli.py`) |

## Future Plans (Roadmap)

We are actively working on expanding ArtifactX. Here is what's coming next:

- [ ] **Enterprise Edition:** Advanced Organization management, SSO (SAML/OIDC), and granular custom roles.
- [ ] **Cross-Platform Apps:** Tauri 2 wrappers for Windows, macOS, Linux, Android, and iOS.
- [ ] **Expanded Intelligence:** Direct integration with NVD, CISA KEV, and FIRST EPSS databases.
- [ ] **CI/CD Integrations:** Native GitHub App and GitLab CI/CD components for automated pipeline scanning.
- [ ] **Notifications:** Slack, Microsoft Teams, and Email alerts for critical findings.
- [ ] **Jira Integration:** Automatically sync remediation tasks with Jira issues.

##  Quick Start (Docker)

The fastest way to run ArtifactX is using Docker.

```bash
# 1. Clone the repository
git clone https://github.com/mrcyberpulse/artifactx.git
cd artifactx

# 2. Start the stack (Frontend, Backend, Postgres, Redis)
docker-compose up -d --build

Frontend GUI: http://localhost:5173

Backend API Docs (Swagger): http://localhost:8000/api/docs
 Local Development Setup
Backend
bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # Edit DB credentials
alembic upgrade head
uvicorn app.main:app --reload
Frontend
cd frontend
npm install
npm run dev
🤝 Contributing
We love open-source! Please read our CONTRIBUTING.md and CODE_OF_CONDUCT.md to get started.
Check out the Issues tab for good first issue labels.

 Security
For security disclosures, please read SECURITY.md.

 License
This project is licensed under the MIT License - see the LICENSE file for details.

ArtifactX v1.0.0 | Created by  MR Cyber Pulse (Harsh saini) | Open-Source SBOM Intelligence Platform
