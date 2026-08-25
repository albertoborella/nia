# ADR-002: Authentication Strategy

**Date:** 2026-08-25
**Status:** Accepted
**Deciders:** Alberto Borella

---

## Context

NIA is an internal admin tool with two roles: Director (full access) and Collaborator (limited to uploading and viewing own notes). Authentication must be:

- Secure against XSS and CSRF (internal tool with sensitive editorial content)
- Stateless to support horizontal scaling without session stores
- Simple to implement for a small team
- Compatible with cookie-based flows for SvelteKit SSR

The system does not require SSO, external identity providers, or multi-tenant isolation.

## Decision

**JWT with HTTP-only cookies + Role-Based Access Control (RBAC)**

| Component | Implementation |
|-----------|---------------|
| Token type | JWT (HS256, configurable algorithm) |
| Access token | 15-minute expiry, stored in `httpOnly` + `secure` + `sameSite=lax` cookie |
| Refresh token | 7-day expiry, separate `httpOnly` cookie, scoped to `/api/v1/auth/refresh` |
| Password hashing | bcrypt with cost factor 12+ |
| RBAC | Two roles: `director` (full), `colaborador` (upload + read own) |
| Cookie path scoping | `access_token` on `/api`, `refresh_token` on `/api/v1/auth/refresh` |

### Token Flow

```
Login → bcrypt verify → generate access (15min) + refresh (7d) → set both cookies
Every request → extract access_token from cookie → validate JWT → if expired, use refresh
Refresh flow → validate refresh_token → issue new access_token → set cookie → retry original
Logout → clear both cookies
```

## Alternatives Considered

### Session-based Authentication (Server-side Sessions)
- **Pros:** Simple revocation, no token complexity.
- **Cons:** Requires session store (Redis/DB), sticky sessions or shared store for horizontal scaling, server-side state contradicts the stateless backend principle.
- **Verdict:** Rejected — adds infrastructure dependency and violates the stateless backend design principle.

### OAuth2 / External Identity Provider
- **Pros:** Enterprise SSO, delegated auth, multi-tenant support.
- **Cons:** Over-engineered for a small internal tool with 2-5 users, adds external dependency, requires redirect flows that complicate SvelteKit SSR.
- **Verdict:** Rejected — not justified for internal use with a handful of users.

### API Key Authentication
- **Pros:** Simple to implement.
- **Cons:** No automatic expiry, harder to revoke per-session, typically stored client-side, no refresh mechanism. Better for machine-to-machine than human users.
- **Verdict:** Rejected — inappropriate for interactive browser-based sessions.

## Consequences

**Positive:**
- Stateless auth: no session store required, server scales horizontally freely
- httpOnly cookies: tokens invisible to JavaScript, eliminating XSS token theft
- Scoped cookie paths minimize attack surface: refresh cookie only sent on refresh endpoint
- SameSite=lax provides baseline CSRF protection for state-changing requests
- Short access token (15min) limits damage window if cookie is compromised

**Negative:**
- JWT cannot be server-side revoked before expiry (only on next refresh attempt)
- Requires refresh token rotation logic in both backend and frontend
- Cookie-based JWT is slightly more complex to debug than header-based auth
- Need middleware to handle automatic refresh-and-retry on 401

**Mitigations:**
- Refresh token acts as revocation mechanism: clear refresh cookie = effective logout
- 15-minute access token window limits exposure
- Future enhancement: add a token blacklist table if real-time revocation is needed
