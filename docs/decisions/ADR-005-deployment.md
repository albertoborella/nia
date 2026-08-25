# ADR-005: Deployment Strategy

**Date:** 2026-08-25
**Status:** Accepted
**Deciders:** Alberto Borella

---

## Context

NIA needs a deployment strategy that is:

- Simple enough for a solo developer to manage
- Reproducible across environments (dev, staging, production)
- Cost-effective for a small internal tool
- Compatible with the chosen stack (Python, Node.js, PostgreSQL)

The team does not need auto-scaling, blue-green deployments, or complex orchestration. A single-server deployment with containers is sufficient.

## Decision

**Podman containers + AWS ECR Public images + Docker Compose**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Container runtime | Podman | Daemonless, rootless, Docker-compatible, more secure defaults |
| Base images | AWS ECR Public | No authentication required, avoids Docker Hub rate limits |
| Orchestration | Docker Compose (podman-compose) | Simple multi-container management, single-file config |
| Reverse proxy | Nginx or Caddy | TLS termination, static file serving, API proxying |
| Database | PostgreSQL 16 in container | Consistent across dev and production |

### Image Registry

| Service | Base Image |
|---------|-----------|
| Backend | `public.ecr.aws/docker/library/python:3.12-slim` |
| Frontend | `public.ecr.aws/docker/library/node:22-slim` |
| PostgreSQL | `public.ecr.aws/docker/library/postgres:16` |
| Nginx | `public.ecr.aws/docker/library/nginx:alpine` |

### Production Architecture

```
┌─────────────────────────────────────────────┐
│  Server / VM                                │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  Nginx (reverse proxy)                │  │
│  │  - TLS termination (port 443)         │  │
│  │  - Static files (frontend build)      │  │
│  │  - Proxy /api → backend:8000          │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ frontend │  │ backend  │  │ postgres │  │
│  │ (build)  │  │ :8000    │  │ :5432    │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                             │
│  Volumes: pgdata, uploads                   │
└─────────────────────────────────────────────┘
```

## Alternatives Considered

### Kubernetes (K8s)
- **Pros:** Auto-scaling, rolling updates, self-healing, production-grade orchestration.
- **Cons:** Massive operational overhead for a single-server app, requires cluster management expertise, overkill for 2-5 users, adds infrastructure cost.
- **Verdict:** Rejected — complexity not justified for the scale.

### Serverless (Lambda / Cloud Functions)
- **Pros:** No server management, auto-scaling, pay-per-use.
- **Cons:** Cold start latency for AI calls, limited to 15-minute execution, complex local development, vendor lock-in, PostgreSQL connection management issues.
- **Verdict:** Rejected — latency and execution limits conflict with long-running AI calls.

### Traditional VMs (No Containers)
- **Pros:** Simpler mental model, no container learning curve.
- **Cons:** Environment drift between dev and production, manual dependency management, harder to replicate issues, no isolation between services.
- **Verdict:** Rejected — containers provide reproducibility with minimal overhead.

## Consequences

**Positive:**
- podman-compose provides one-command environment setup (`podman-compose up -d`)
- Rootless containers improve security posture (no root daemon)
- AWS ECR Public images eliminate Docker Hub authentication and rate limits
- Reproducible environments: dev matches production via identical container configs
- Alembic migrations integrated into deployment workflow
- Volume mounts for database persistence and file uploads

**Negative:**
- Podman has smaller community than Docker; fewer Stack Overflow answers
- Container orchestration is single-server only (no built-in HA)
- PostgreSQL in container requires careful volume management for data persistence
- Manual TLS certificate management (Let's Encrypt or similar)

**Mitigations:**
- podman-compose is CLI-compatible with docker-compose; team can fall back to Docker if needed
- Single-server is appropriate for internal tool; HA not required for MVP
- Automated backup script handles database and file persistence
- Caddy alternative provides automatic TLS without manual certificate management
