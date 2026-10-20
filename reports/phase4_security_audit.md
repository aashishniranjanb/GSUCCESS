# GPAT Learning OS — Phase 4: API & Security Audit Report

**Date:** 2026-10-19  
**Scope:** Endpoint Authorization, Credential Exposure, Session Handling, and Security Boundaries  
**Status:** PASS WITH DOCUMENTED LIMITATIONS  

---

## 1. Security Architecture & Boundary Analysis

### A. Client Secrets & Environment Exposure
- **Audit:** Searched `web/src` for leaked API keys, tokens, and database credentials.
- **Finding:** Clean. Zero service keys, secret keys, or database credentials exist in client-side code.
- **Environment Variables:** Only standard `NEXT_PUBLIC_API_URL` is referenced for relative/custom API proxying.

### B. Admin API Protection
- **Mechanism:** Protected endpoints (`/api/admin/dashboard`, `/api/admin/backup/*`, `/api/admin/pilot/*`) require `verify_admin_access`.
- **Enforcement:** Validates `X-Admin-Secret` header or HTTP Basic Auth.
- **Fail-Closed Policy:** In production (`ENVIRONMENT=production`), the application strictly halts with HTTP 500 if `ADMIN_SECRET` is not configured.

### C. CORS Configuration
- Configured dynamically via `ALLOWED_ORIGINS`.
- In production (`ENVIRONMENT=production`), wildcard `*` is explicitly disabled; origins fail-closed to empty array if unconfigured.

### D. Supabase Auth Status & Learner-Level Authorization
- **Status:** *Designated Architecture / Staging Preparation*.
- **Current State:** The application operates on a pseudonymous learner identifier model (`student_id="student_01"`).
- **Security Gap (Documented):** While Supabase Auth is the designated provider for VPS hosting, token verification at the FastAPI gateway is currently operating in local pilot mode. In production, Supabase JWT verification must be enforced on every mutation endpoint to prevent arbitrary `student_id` parameter overrides.

---

## 2. Security Recommendations for Production Deployment
1. **JWT Verification Middleware:** Add `PyJWT` or `supabase-py` token validation on FastAPI to verify `Authorization: Bearer <jwt>` and map `student_id` strictly from token claims (`sub`).
2. **Rate Limiting:** Implement token bucket rate limiting on `POST /api/study/attempt` and `POST /api/mock/create` to prevent automated scraping of the question bank.
3. **Database Permissions:** Set file permissions `chmod 600 gpat_knowledge.db` on VPS host so only the application user can access the database files.
