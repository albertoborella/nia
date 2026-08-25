# Logging Strategy — NIA

## Logging Philosophy

### Core Principles

1. **Log with purpose**: Every log entry must serve debugging, auditing, or monitoring. No noise.
2. **Structured from day one**: All logs are machine-parseable JSON. Human-readable formatting is a development convenience, not a production format.
3. **Never log secrets**: Passwords, tokens, API keys, PII, and AI prompt content are forbidden from logs. See the "Sensitive Data" section for the full list.
4. **Correlate everything**: Every log entry carries a correlation ID so requests can be traced end-to-end across frontend, backend, and AI calls.
5. **Audit separately**: Business-critical actions (CRUD, auth events, AI usage) go to a dedicated audit stream with different retention policies.

---

## Log Levels

| Level | When to Use | Examples |
|-------|-------------|----------|
| **DEBUG** | Detailed diagnostic information. Disabled in production by default. | SQL query text, request body before validation, AI prompt construction steps |
| **INFO** | Normal operational events. The system is doing what it should. | Request completed, boletin created, user logged in, AI call succeeded |
| **WARN** | Unexpected but recoverable. Something is off, but the system continues. | Slow query (>500ms), retry attempt, AI rate limit approaching, deprecated endpoint used |
| **ERROR** | Failures that need human attention. The operation failed. | AI service unavailable, database connection lost, unhandled exception, file upload failed |
| **CRITICAL** | System-threatening failures. Immediate intervention required. | Database unreachable, JWT signing key missing, all worker processes down |

### Level Configuration by Environment

| Environment | Minimum Level | Rationale |
|-------------|---------------|-----------|
| Development | DEBUG | Full visibility during local work |
| Staging | INFO | Realistic production-like behavior |
| Production | INFO | Noise reduction; DEBUG enabled on-demand per logger |

---

## Structured Logging Format

### JSON Log Schema

Every log entry is a single JSON object written to stdout (one per line):

```json
{
  "timestamp": "2026-08-25T14:32:01.123Z",
  "level": "INFO",
  "logger": "nia.api.request",
  "message": "Request completed",
  "service": "nia-backend",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "request_id": "req-8f14e45f",
  "method": "POST",
  "path": "/api/v1/incidentes/consultar",
  "status_code": 200,
  "duration_ms": 1243,
  "ip": "192.168.1.100"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | When the event occurred (UTC) |
| `level` | string | `DEBUG`, `INFO`, `WARN`, `ERROR`, `CRITICAL` |
| `message` | string | Human-readable description of the event |
| `service` | string | Originating service: `nia-backend`, `nia-frontend` |
| `correlation_id` | UUID | Ties all logs from a single request together |

### Optional Fields

| Field | Type | When Present |
|-------|------|--------------|
| `user_id` | UUID | Authenticated request |
| `request_id` | string | Unique request identifier |
| `duration_ms` | integer | Operation timing |
| `error_code` | string | NIA error code (e.g., `AI_UNAVAILABLE`) |
| `method` | string | HTTP method |
| `path` | string | Request path |
| `status_code` | integer | HTTP response status |
| `ip` | string | Client IP (masked in logs if needed) |
| `ai_tokens_used` | integer | Token count from AI response |
| `ai_model` | string | Model used for AI call |
| `ai_duration_ms` | integer | Time spent in AI call |

---

## Backend Logging (FastAPI)

### Request/Response Logging

All HTTP requests are logged automatically via middleware:

```python
# backend/app/middleware/logging.py

import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("nia.api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        user_id = getattr(request.state, "user_id", None)

        request.state.correlation_id = correlation_id
        request.state.request_id = request_id

        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000)

        log_data = {
            "correlation_id": correlation_id,
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "ip": request.client.host if request.client else None,
        }

        if user_id:
            log_data["user_id"] = user_id

        if duration_ms > 500:
            logger.warning("Slow request", extra={**log_data, "slow": True})
        elif response.status_code >= 500:
            logger.error("Server error", extra=log_data)
        else:
            logger.info("Request completed", extra=log_data)

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-ID"] = request_id

        return response
```

### Database Query Logging

SQL queries are logged at DEBUG level with duration tracking:

```python
# backend/app/database.py

import logging
import time
from sqlalchemy import event

logger = logging.getLogger("nia.db")


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    start_times = conn.info.get("query_start_time", [])
    if start_times:
        duration_ms = round((time.perf_counter() - start_times.pop()) * 1000)
        logger.debug(
            "SQL query executed",
            extra={
                "duration_ms": duration_ms,
                "rows_affected": cursor.rowcount,
                "query": statement[:200],  # Truncate long queries
            }
        )
        if duration_ms > 500:
            logger.warning(
                "Slow SQL query",
                extra={
                    "duration_ms": duration_ms,
                    "query": statement[:200],
                }
            )
```

### AI Service Call Logging

Every AI interaction is logged for cost tracking and auditing (RNF-06.4):

```python
# backend/app/services/ia_service.py

import logging
import time

logger = logging.getLogger("nia.ai")


async def call_ai_api(prompt: str, config: dict) -> dict:
    start_time = time.perf_counter()
    model = config.get("modelo", settings.IA_MODEL)

    logger.info(
        "AI call started",
        extra={
            "ai_model": model,
            "ai_max_tokens": config.get("max_tokens", 2000),
            "ai_temperature": config.get("temperatura", 0.3),
        }
    )

    try:
        response = await _execute_ai_request(prompt, config)
        duration_ms = round((time.perf_counter() - start_time) * 1000)
        tokens_used = response.get("usage", {}).get("total_tokens", 0)

        logger.info(
            "AI call completed",
            extra={
                "ai_model": model,
                "ai_tokens_used": tokens_used,
                "ai_duration_ms": duration_ms,
            }
        )

        return response

    except AIServiceError as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000)
        logger.error(
            "AI call failed",
            extra={
                "ai_model": model,
                "ai_duration_ms": duration_ms,
                "error_code": e.code,
                "error_message": str(e),
            }
        )
        raise
```

### Authentication Events

Auth events are always logged at INFO level for security auditing:

```python
# backend/app/services/auth_service.py

import logging

audit_logger = logging.getLogger("nia.audit.auth")


def authenticate_user(db: Session, email: str, password: str) -> dict:
    user = db.query(Usuario).filter(Usuario.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        audit_logger.warning(
            "Login failed",
            extra={
                "email": email,
                "reason": "invalid_credentials",
                "ip": get_client_ip(),
            }
        )
        raise AuthenticationError("Invalid email or password")

    audit_logger.info(
        "Login successful",
        extra={
            "user_id": str(user.id),
            "email": email,
            "ip": get_client_ip(),
        }
    )

    return create_tokens(user)
```

### Business Logic Events

Key domain actions are logged for operational visibility:

```python
# backend/app/services/boletin_service.py

import logging

logger = logging.getLogger("nia.business")


def create_boletin(db: Session, data: BoletinCreate, user_id: str) -> Boletin:
    boletin = Boletin(**data.model_dump(), created_by=user_id)
    db.add(boletin)
    db.commit()

    logger.info(
        "Bulletin created",
        extra={
            "boletin_id": str(boletin.id),
            "periodo": data.periodo,
            "user_id": user_id,
        }
    )
    return boletin


def close_boletin(db: Session, boletin_id: str, user_id: str) -> Boletin:
    boletin = db.query(Boletin).filter(Boletin.id == boletin_id).first()
    boletin.estado = "cerrado"
    db.commit()

    logger.info(
        "Bulletin closed",
        extra={
            "boletin_id": boletin_id,
            "user_id": user_id,
            "secciones_completadas": count_complete_sections(boletin),
        }
    )
    return boletin
```

---

## Frontend Logging (SvelteKit)

### Client-Side Error Reporting

Frontend errors are captured and sent to the backend for centralized logging:

```typescript
// frontend/src/lib/utils/logger.ts

import { browser } from '$app/environment';

interface LogEntry {
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
  message: string;
  service: 'nia-frontend';
  timestamp: string;
  url?: string;
  line?: number;
  column?: number;
  stack?: string;
  component?: string;
}

class FrontendLogger {
  private buffer: LogEntry[] = [];
  private flushInterval = 5000;
  private maxBufferSize = 50;

  constructor() {
    if (browser) {
      this.setupErrorHandlers();
      this.startFlushTimer();
    }
  }

  private setupErrorHandlers() {
    window.addEventListener('error', (event) => {
      this.log('ERROR', event.message, {
        url: event.filename,
        line: event.lineno,
        column: event.colno,
        stack: event.error?.stack,
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.log('ERROR', `Unhandled promise rejection: ${event.reason}`, {
        stack: event.reason?.stack,
      });
    });
  }

  log(level: LogEntry['level'], message: string, extra?: Partial<LogEntry>) {
    const entry: LogEntry = {
      level,
      message,
      service: 'nia-frontend',
      timestamp: new Date().toISOString(),
      ...extra,
    };

    this.buffer.push(entry);

    if (level === 'ERROR' || this.buffer.length >= this.maxBufferSize) {
      this.flush();
    }
  }

  private async flush() {
    if (this.buffer.length === 0) return;

    const entries = [...this.buffer];
    this.buffer = [];

    try {
      await fetch('/api/v1/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entries }),
        keepalive: true,
      });
    } catch {
      // Silent fail — logging should never break the app
    }
  }

  private startFlushTimer() {
    setInterval(() => this.flush(), this.flushInterval);
  }
}

export const logger = new FrontendLogger();
```

### Performance Metrics

Page load and navigation timing:

```typescript
// frontend/src/lib/utils/performance.ts

import { logger } from './logger';

export function logNavigation(from: string, to: string, duration_ms: number) {
  logger.info('Navigation', {
    message: `Navigated from ${from} to ${to}`,
    duration_ms,
  } as any);
}

export function logComponentRender(component: string, duration_ms: number) {
  logger.debug(`Component rendered: ${component}`, {
    duration_ms,
  } as any);
}
```

---

## Audit Logging

Audit logs are a separate stream from application logs. They track who did what, when, and on which resource.

### Audit Log Schema

```json
{
  "timestamp": "2026-08-25T14:32:01.123Z",
  "event": "boletin.closed",
  "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_email": "director@nia.org",
  "resource_type": "boletin",
  "resource_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "action": "close",
  "changes": {
    "estado": { "from": "borrador", "to": "cerrado" }
  },
  "ip": "192.168.1.100",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Event Categories

| Category | Events | Example |
|----------|--------|---------|
| **Authentication** | `auth.login`, `auth.login_failed`, `auth.logout`, `auth.refresh`, `auth.password_change` | User logged in |
| **Authorization** | `auth.access_denied` | Collaborator tried to access director-only endpoint |
| **CRUD** | `{resource}.created`, `{resource}.updated`, `{resource}.deleted` | Boletin created |
| **State transitions** | `{resource}.state_changed` | Boletin closed |
| **AI usage** | `ai.call`, `ai.call_failed` | AI article generated |
| **File operations** | `file.uploaded`, `file.deleted` | Note uploaded |

### Audit Logger Implementation

```python
# backend/app/middleware/audit.py

import logging
from typing import Optional

audit_logger = logging.getLogger("nia.audit")


def log_audit_event(
    event: str,
    user_id: Optional[str],
    user_email: Optional[str],
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    action: Optional[str] = None,
    changes: Optional[dict] = None,
    ip: Optional[str] = None,
    correlation_id: Optional[str] = None,
):
    """Write a structured audit event."""
    entry = {
        "event": event,
        "user_id": user_id,
        "user_email": user_email,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "action": action,
        "changes": changes,
        "ip": ip,
        "correlation_id": correlation_id,
    }
    audit_logger.info(event, extra=entry)
```

### AI Prompt Usage Auditing

AI calls are logged with sanitized metadata — never the full prompt or response content:

```python
# Logged for every AI call:
# - Model used
# - Token count (input + output)
# - Duration
# - Whether it succeeded or failed
# - Which prompt template was used (not the rendered prompt)

log_audit_event(
    event="ai.call",
    user_id=user_id,
    resource_type="prompt",
    resource_id=prompt_template_id,
    action="generate_article",
    changes={
        "ai_model": "gpt-4",
        "ai_tokens_used": 1523,
        "ai_duration_ms": 4200,
    },
)
```

---

## Log Destinations

### Development

Structured JSON to stdout with optional color formatting:

```python
# backend/app/config/logging.py

import logging
import json
import sys
from datetime import datetime, timezone


class ColorFormatter(logging.Formatter):
    """Human-readable colored output for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[41m",  # White on Red
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
        return (
            f"{color}{timestamp} [{record.levelname:<7}] "
            f"{record.name}: {record.getMessage()}{self.RESET}"
        )


class JSONFormatter(logging.Formatter):
    """Structured JSON output for production."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "nia-backend",
        }

        # Merge extra fields
        for key in [
            "correlation_id", "user_id", "request_id", "duration_ms",
            "error_code", "method", "path", "status_code", "ip",
            "ai_model", "ai_tokens_used", "ai_duration_ms",
        ]:
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_entry, default=str)
```

### Production Configuration

```python
def setup_logging(environment: str = "development"):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if environment == "development" else logging.INFO)

    # Remove default handlers
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if environment == "development":
        handler.setFormatter(ColorFormatter())
    else:
        handler.setFormatter(JSONFormatter())

    root.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

### Audit Log Stream

Audit logs go to a separate file in production for independent retention:

```python
def setup_audit_logging(log_dir: str = "/var/log/nia"):
    import os
    os.makedirs(log_dir, exist_ok=True)

    audit_handler = logging.FileHandler(f"{log_dir}/audit.jsonl")
    audit_handler.setFormatter(JSONFormatter())

    audit_logger = logging.getLogger("nia.audit")
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False  # Don't duplicate to stdout
```

---

## Correlation and Tracing

### Request Correlation

Every request gets a correlation ID. The frontend generates it; the backend propagates it:

```
Browser                          Backend                         AI Service
   │                                │                                │
   │  X-Correlation-ID: uuid-abc    │                                │
   │ ──────────────────────────────>│                                │
   │                                │  X-Correlation-ID: uuid-abc   │
   │                                │ ─────────────────────────────>│
   │                                │                                │
   │  X-Correlation-ID: uuid-abc    │                                │
   │ <──────────────────────────────│                                │
```

### Frontend Propagation

```typescript
// frontend/src/lib/api/client.ts

class APIClient {
  private correlationId: string | null = null;

  private getCorrelationId(): string {
    if (!this.correlationId) {
      this.correlationId = crypto.randomUUID();
    }
    return this.correlationId;
  }

  private async request<T>(method: string, path: string): Promise<T> {
    const response = await fetch(`/api/v1${path}`, {
      method,
      headers: {
        'X-Correlation-ID': this.getCorrelationId(),
      },
    });
    // ...
  }
}
```

### AI Call Tracing

AI calls inherit the correlation ID from the originating request:

```python
async def call_ai_api(prompt: str, config: dict, correlation_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.IA_API_KEY}",
                "X-Correlation-ID": correlation_id,
            },
            json=payload,
        )
```

---

## Log Rotation and Retention

### Application Logs

| Policy | Value |
|--------|-------|
| Rotation | Daily or when file reaches 50 MB |
| Retention | 30 days |
| Compression | gzip for archived logs |
| Location | `/var/log/nia/application/` |

### Audit Logs

| Policy | Value |
|--------|-------|
| Rotation | Daily |
| Retention | 1 year (minimum) |
| Compression | gzip |
| Location | `/var/log/nia/audit/` |
| Archival | After 90 days, archive to cold storage (S3-compatible) |

### Retention Configuration

```bash
# /etc/logrotate.d/nia
/var/log/nia/application/*.jsonl {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}

/var/log/nia/audit/*.jsonl {
    daily
    missingok
    rotate 365
    compress
    delaycompress
    notifempty
    copytruncate
}
```

---

## Monitoring and Alerting

### Error Rate Monitoring

Alert thresholds based on error frequency:

| Condition | Severity | Action |
|-----------|----------|--------|
| >5 `ERROR` logs per minute | WARN | Investigate within 1 hour |
| >20 `ERROR` logs per minute | ERROR | Investigate immediately |
| >50 `ERROR` logs per minute | CRITICAL | Page on-call |
| Any `CRITICAL` log | CRITICAL | Page on-call |

### Performance Metrics

Logged at INFO level for analysis:

| Metric | Threshold | Log Level |
|--------|-----------|-----------|
| API request duration | >500ms | WARN |
| AI call duration | >30s | WARN |
| AI call duration | >60s | ERROR |
| Database query | >500ms | WARN |
| File upload | >10s | WARN |

### Health Check Logging

Health check results are logged periodically:

```python
# backend/app/routers/health.py

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    checks = perform_health_checks(db)
    status = "healthy" if all(c == "ok" for c in checks.values()) else "degraded"

    logger.info(
        "Health check",
        extra={
            "health_status": status,
            "db_ok": checks.get("database") == "ok",
            "ai_ok": checks.get("ai") == "ok",
        }
    )

    return {"status": status, "checks": checks}
```

---

## Sensitive Data Rules

### What NOT to Log

| Data Type | Reason |
|-----------|--------|
| Passwords (plain or hashed) | Credential exposure |
| JWT tokens (access or refresh) | Session hijacking risk |
| API keys (`IA_API_KEY`) | Credential exposure |
| AI prompt content | May contain user data |
| AI response content | May contain PII |
| File contents | Data exposure |
| Database query parameters | SQL injection aid |
| `DATABASE_URL` | Contains credentials |
| Internal file paths | Information disclosure |

### What TO Log

| Data Type | When |
|-----------|------|
| `user_id` (UUID) | Authenticated requests |
| Action performed | All audit events |
| Resource IDs | CRUD operations |
| Timestamp | Always |
| IP address | Auth events (mask if needed) |
| Error code | Errors and warnings |
| Duration | Operations with timing |
| Token count (AI) | Cost tracking |

---

## Summary

| Aspect | Decision |
|--------|----------|
| Format | Structured JSON (production), colored text (development) |
| Transport | stdout → log aggregator or file |
| Correlation | UUID per request, propagated across services |
| Audit | Separate logger, separate file, 1-year retention |
| Retention | 30 days application, 1 year audit |
| Rotation | Daily, 50 MB cap |
| AI logging | Model, tokens, duration — never prompt content |
| Sensitive data | Never log passwords, tokens, keys, or PII |
| Frontend errors | Buffered and flushed to backend `/api/v1/logs` |

For error codes and HTTP status mapping, refer to `04-error-handling.md`.
For security model details, refer to `02-security.md`.
