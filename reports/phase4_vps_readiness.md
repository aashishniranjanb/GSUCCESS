# GPAT Learning OS — Phase 4: VPS Deployment Readiness Report

**Date:** 2026-10-19  
**Scope:** Production Hosting Architecture, Process Supervision, Reverse Proxy, and SQLite Backup Strategy  
**Status:** READY FOR STAGING DEPLOYMENT  

---

## 1. Hosting Architecture Specification

- **Target Host:** Virtual Private Server (Ubuntu 24.04 LTS / Debian 12 recommended).
- **Process Supervision:** Systemd units or Docker Compose:
  1. `gpat-backend`: Uvicorn ASGI server running `backend.main:app` (4 workers, bound to `127.0.0.1:8000`).
  2. `gpat-frontend`: Next.js production server running `npm start` (bound to `127.0.0.1:3000`).
- **Reverse Proxy & SSL:**
  - Nginx handling TLS termination (Let's Encrypt / Certbot).
  - Proxy `/api/` traffic to `http://127.0.0.1:8000`.
  - Proxy all other traffic to `http://127.0.0.1:3000`.
  - HTTP/2 enabled, Brotli/Gzip compression enabled for static chunks.

---

## 2. Environment Configuration & Secret Management

| Environment Variable | Target / Purpose | Security Requirement |
|---|---|---|
| `ENVIRONMENT` | Set to `production` | Fails closed if admin secret is missing; disables open CORS wildcard. |
| `ADMIN_SECRET` | 32+ character high-entropy secret | Stored in `.env` on server with `chmod 600`. Never committed to Git. |
| `ALLOWED_ORIGINS` | Explicit domain list (e.g. `https://gpat.domain.com`) | Strict CORS control. |
| `GPAT_DB_PATH` | Absolute path to `gpat_knowledge.db` | Dedicated persistent storage mount. |
| `GPAT_BASELINE_DB_PATH` | Absolute path to `data/gpat_baseline.db` | Read-only permissions on baseline content. |

---

## 3. Persistent SQLite Strategy & Backup Cadence

- **Why SQLite on VPS:** SQLite delivers sub-millisecond retrieval latency with zero network overhead, perfectly matching high-frequency active recall question delivery.
- **Backup Automation:**
  - Cron job configured: `0 2 * * * /path/to/.venv/bin/python /path/to/scripts/backup_db.py`
  - Automated compressed snapshot (`.db.gz`) created nightly with SHA-256 checksum validation.
- **PostgreSQL Cutover Policy:** PostgreSQL migration remains an isolated pilot experiment (`backend/migrate_to_supabase.py`) and is **not** required for production staging. SQLite is the verified, authoritative engine.
