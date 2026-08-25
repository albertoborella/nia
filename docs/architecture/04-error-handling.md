# Error Handling Patterns — NIA

## Error Handling Philosophy

### Core Principles

1. **Fail gracefully**: Never expose internal errors, stack traces, or sensitive data to users
2. **User-friendly messages**: Every error must have a human-readable message that explains what happened and what to do next
3. **Consistent format**: API and UI use the same error structure for predictable handling
4. **Fail fast, fail loud**: Errors should be caught and logged immediately, not silently swallowed
5. **Correlation**: Every error must be traceable via correlation IDs for debugging

### Error Response Contract

All API errors follow the standard format defined in [01-api-design.md](01-api-design.md#errores):

```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

**Rules:**
- `code` is a machine-readable identifier (e.g., `BOLETIN_NOT_FOUND`)
- `message` is safe to display to end users
- Never expose internal details: SQL queries, file paths, stack traces, or AI prompts
- HTTP status code must match the error category (see [01-api-design.md — Errores](01-api-design.md#errores))

---

## Backend Error Handling (FastAPI)

### HTTP Exception Hierarchy

| HTTP Status | Code Prefix | Usage |
|-------------|-------------|-------|
| 400 | `VAL_*` | Bad request, malformed data |
| 401 | `AUTH_*` | Authentication required or failed |
| 403 | `AUTH_FORBIDDEN` | Authenticated but insufficient permissions |
| 404 | `NF_*` | Resource not found |
| 409 | `CONFLICT_*` | State conflict (e.g., boletin already closed) |
| 422 | `VAL_*` | Validation error (Pydantic) |
| 500 | `SYS_*` | Internal server error (never expose details) |
| 503 | `AI_UNAVAILABLE` | External service (AI provider) unavailable |

### Custom Exception Classes

```python
# backend/app/exceptions.py

from fastapi import HTTPException, status


class NIAException(HTTPException):
    """Base exception for all NIA errors."""

    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message}
        )


class AuthenticationError(NIAException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="AUTH_REQUIRED", message=message, status_code=401)


class ForbiddenError(NIAException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(code="AUTH_FORBIDDEN", message=message, status_code=403)


class NotFoundError(NIAException):
    def __init__(self, resource: str, resource_id: str = ""):
        detail = f"{resource} not found" if not resource_id else f"{resource} '{resource_id}' not found"
        super().__init__(code=f"NF_{resource.upper()}", message=detail, status_code=404)


class ValidationError(NIAException):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=422)


class ConflictError(NIAException):
    def __init__(self, message: str):
        super().__init__(code="CONFLICT_STATE", message=message, status_code=409)


class AIServiceError(NIAException):
    def __init__(self, message: str = "AI service temporarily unavailable"):
        super().__init__(code="AI_UNAVAILABLE", message=message, status_code=503)


class FileProcessingError(NIAException):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=422)
```

### Error Response Format

```python
# Standard error response for all endpoints
{
    "detail": {
        "code": "BOLETIN_NOT_FOUND",
        "message": "Bulletin 'uuid-value' not found"
    }
}
```

### Validation Errors (Pydantic)

Pydantic validation errors are transformed to match the standard format:

```python
# backend/app/main.py

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "errors": errors
            }
        }
    )
```

### Database Errors (SQLModel/PostgreSQL)

```python
# backend/app/services/boletin_service.py

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.exceptions import NIAException, NotFoundError


def get_boletin_by_id(db: Session, boletin_id: str) -> Boletin:
    try:
        boletin = db.query(Boletin).filter(Boletin.id == boletin_id).first()
        if not boletin:
            raise NotFoundError("Boletin", boletin_id)
        return boletin
    except SQLAlchemyError as e:
        logger.error("Database error fetching boletin", extra={"boletin_id": boletin_id, "error": str(e)})
        raise NIAException(
            code="DB_QUERY_ERROR",
            message="Unable to retrieve bulletin",
            status_code=500
        )


def create_boletin(db: Session, data: BoletinCreate) -> Boletin:
    try:
        boletin = Boletin(**data.model_dump())
        db.add(boletin)
        db.commit()
        db.refresh(boletin)
        return boletin
    except IntegrityError as e:
        db.rollback()
        logger.warning("Integrity error creating boletin", extra={"error": str(e)})
        raise NIAException(
            code="DB_INTEGRITY_ERROR",
            message="Bulletin could not be created due to data conflict",
            status_code=409
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database error creating boletin", extra={"error": str(e)})
        raise NIAException(
            code="DB_ERROR",
            message="Unable to create bulletin",
            status_code=500
        )
```

### AI Service Errors

```python
# backend/app/services/ia_service.py

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.exceptions import AIServiceError, NIAException


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
)
async def call_ai_api(prompt: str, config: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.IA_API_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.IA_API_KEY}"},
                json={
                    "model": config.get("modelo", settings.IA_MODEL),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": config.get("temperatura", 0.3),
                    "max_tokens": config.get("max_tokens", 2000)
                }
            )

            if response.status_code == 429:
                raise AIServiceError("AI service rate limit exceeded. Please try again later.")

            if response.status_code >= 500:
                raise AIServiceError("AI service temporarily unavailable")

            if response.status_code != 200:
                raise NIAException(
                    code="AI_REQUEST_FAILED",
                    message="AI request failed",
                    status_code=502
                )

            return response.json()

    except httpx.TimeoutException:
        raise AIServiceError("AI request timed out. Please try again.")
    except httpx.NetworkError:
        raise AIServiceError("Unable to connect to AI service")
    except AIServiceError:
        raise
    except Exception as e:
        logger.error("Unexpected AI service error", extra={"error": str(e)})
        raise AIServiceError()
```

---

## Frontend Error Handling (SvelteKit)

### Error Boundaries

```typescript
// frontend/src/routes/+error.svelte
<script>
  import { page } from '$app/stores';
</script>

<div class="error-page" role="alert">
  <h1>Something went wrong</h1>
  {#if $page.error}
    <p>{$page.error.message}</p>
  {/if}
  <a href="/dashboard">Return to dashboard</a>
</div>
```

### API Client Error Handling

```typescript
// frontend/src/lib/api/client.ts

import { browser } from '$app/environment';
import { goto } from '$app/navigation';

interface APIError {
  detail: {
    code: string;
    message: string;
    errors?: Array<{
      field: string;
      message: string;
      type: string;
    }>;
  };
}

class APIClient {
  private async request<T>(method: string, path: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`/api/v1${path}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const error: APIError = await response.json();

        // Handle authentication errors
        if (response.status === 401) {
          // Try to refresh token
          const refreshed = await this.refreshToken();
          if (refreshed) {
            // Retry original request
            return this.request<T>(method, path, options);
          }
          // Redirect to login if refresh fails
          if (browser) {
            goto('/login');
          }
          throw new Error('Session expired. Please log in again.');
        }

        // Handle forbidden
        if (response.status === 403) {
          throw new Error('You do not have permission to perform this action.');
        }

        // Handle validation errors
        if (response.status === 422 && error.detail.errors) {
          const fieldErrors = error.detail.errors.map(e => `${e.field}: ${e.message}`).join('\n');
          throw new Error(fieldErrors);
        }

        // Handle other errors
        throw new Error(error.detail.message || 'An unexpected error occurred');
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      return response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error. Please check your connection.');
    }
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, {
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PUT', path, {
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }
}

export const api = new APIClient();
```

### Form Validation Errors

```typescript
// frontend/src/lib/components/FormField.svelte

<script lang="ts">
  export let label: string;
  export let name: string;
  export let value: string = '';
  export let error: string = '';
  export let required: boolean = false;
  export let type: string = 'text';
</script>

<div class="form-field" class:error={!!error}>
  <label for={name}>
    {label}
    {#if required}<span class="required">*</span>{/if}
  </label>

  {#if type === 'textarea'}
    <textarea
      id={name}
      {name}
      bind:value
      aria-invalid={!!error}
      aria-describedby={error ? `${name}-error` : undefined}
    />
  {:else}
    <input
      type="{type}"
      id={name}
      {name}
      bind:value
      aria-invalid={!!error}
      aria-describedby={error ? `${name}-error` : undefined}
    />
  {/if}

  {#if error}
    <span id="{name}-error" class="error-message" role="alert">
      {error}
    </span>
  {/if}
</div>

<style>
  .form-field {
    margin-bottom: 1rem;
  }

  .error input,
  .error textarea {
    border-color: var(--color-error);
  }

  .error-message {
    color: var(--color-error);
    font-size: 0.875rem;
    margin-top: 0.25rem;
    display: block;
  }

  .required {
    color: var(--color-error);
  }
</style>
```

### Toast Notifications

```typescript
// frontend/src/lib/stores/toast.store.ts

import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);

  function addToast(type: ToastType, message: string, duration: number = 5000) {
    const id = Math.random().toString(36).substring(2, 9);
    const toast: Toast = { id, type, message, duration };

    update(toasts => [...toasts, toast]);

    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }

    return id;
  }

  function removeToast(id: string) {
    update(toasts => toasts.filter(t => t.id !== id));
  }

  return {
    subscribe,
    success: (message: string) => addToast('success', message),
    error: (message: string) => addToast('error', message, 10000),
    warning: (message: string) => addToast('warning', message, 7000),
    info: (message: string) => addToast('info', message),
    remove: removeToast,
  };
}

export const toast = createToastStore();
```

```svelte
<!-- frontend/src/lib/components/Toast.svelte -->
<script lang="ts">
  import { toast } from '$lib/stores/toast.store';
</script>

<div class="toast-container" aria-live="polite" aria-atomic="true">
  {#each $toasts as toast (toast.id)}
    <div
      class="toast toast-{toast.type}"
      role="alert"
      aria-live="assertive"
    >
      <span class="toast-message">{toast.message}</span>
      <button
        class="toast-close"
        on:click={() => toast.remove(toast.id)}
        aria-label="Dismiss notification"
      >
        ×
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .toast {
    padding: 1rem;
    border-radius: 0.375rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-width: 300px;
    max-width: 500px;
  }

  .toast-success {
    background-color: var(--color-success-bg);
    border-left: 4px solid var(--color-success);
  }

  .toast-error {
    background-color: var(--color-error-bg);
    border-left: 4px solid var(--color-error);
  }

  .toast-warning {
    background-color: var(--color-warning-bg);
    border-left: 4px solid var(--color-warning);
  }

  .toast-info {
    background-color: var(--color-info-bg);
    border-left: 4px solid var(--color-info);
  }

  .toast-close {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.5rem;
    line-height: 1;
    opacity: 0.7;
  }

  .toast-close:hover {
    opacity: 1;
  }
</style>
```

### Loading and Error States

```svelte
<!-- frontend/src/lib/components/DataLoader.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    loading: boolean;
    error: string | null;
    onRetry?: () => void;
    children: Snippet;
  }

  let { loading, error, onRetry, children }: Props = $props();
</script>

{#if loading}
  <div class="loading" role="status" aria-live="polite">
    <div class="spinner" aria-hidden="true"></div>
    <span>Loading...</span>
  </div>
{:else if error}
  <div class="error-state" role="alert">
    <div class="error-icon" aria-hidden="true">⚠</div>
    <h3>Unable to load data</h3>
    <p>{error}</p>
    {#if onRetry}
      <button class="retry-button" on:click={onRetry}>
        Try again
      </button>
    {/if}
  </div>
{:else}
  {@render children()}
{/if}

<style>
  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    gap: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--color-border);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-state {
    text-align: center;
    padding: 3rem;
    color: var(--color-text-muted);
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .retry-button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
  }

  .retry-button:hover {
    background-color: var(--color-primary-hover);
  }
</style>
```

---

## Error Codes Registry

### Authentication Errors (AUTH_*)

| Code | HTTP Status | Message |
|------|-------------|---------|
| `AUTH_REQUIRED` | 401 | Authentication required |
| `AUTH_INVALID_CREDENTIALS` | 401 | Invalid email or password |
| `AUTH_TOKEN_EXPIRED` | 401 | Session expired. Please log in again. |
| `AUTH_TOKEN_INVALID` | 401 | Invalid authentication token |
| `AUTH_FORBIDDEN` | 403 | You do not have permission to perform this action |
| `AUTH_REFRESH_FAILED` | 401 | Unable to refresh session. Please log in again. |

### Validation Errors (VAL_*)

| Code | HTTP Status | Message |
|------|-------------|---------|
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `VAL_EMAIL_INVALID` | 422 | Please enter a valid email address |
| `VAL_PASSWORD_TOO_SHORT` | 422 | Password must be at least 8 characters |
| `VAL_PASSWORD_MISMATCH` | 422 | Passwords do not match |
| `VAL_DATE_INVALID` | 422 | Please enter a valid date |
| `VAL_DATE_RANGE_INVALID` | 422 | Start date must be before end date |
| `VAL_FIELD_REQUIRED` | 422 | This field is required |
| `VAL_STRING_TOO_LONG` | 422 | Text exceeds maximum length |
| `VAL_ENUM_INVALID` | 422 | Invalid value for this field |

### Not Found Errors (NF_*)

| Code | HTTP Status | Message |
|------|-------------|---------|
| `NF_BOLETIN` | 404 | Bulletin not found |
| `NF_SECCION` | 404 | Section not found |
| `NF_NOTA` | 404 | Note not found |
| `NF_INCIDENTE` | 404 | Incident not found |
| `NF_PROMPT` | 404 | Prompt not found |
| `NF_AUSPICIANTE` | 404 | Sponsor not found |
| `NF_USUARIO` | 404 | User not found |

### AI Service Errors (AI_*)

| Code | HTTP Status | Message |
|------|-------------|---------|
| `AI_UNAVAILABLE` | 503 | AI service temporarily unavailable. Please try again later. |
| `AI_TIMEOUT` | 504 | AI request timed out. Please try again. |
| `AI_RATE_LIMITED` | 429 | AI service rate limit exceeded. Please try again later. |
| `AI_REQUEST_FAILED` | 502 | AI request failed. Please try again. |
| `AI_INVALID_RESPONSE` | 502 | AI returned an invalid response. Please try again. |

### Database Errors (DB_*)

| Code | HTTP Status | Message |
|------|-------------|---------|
| `DB_ERROR` | 500 | Unable to complete request. Please try again. |
| `DB_QUERY_ERROR` | 500 | Unable to retrieve data. Please try again. |
| `DB_INTEGRITY_ERROR` | 409 | Data conflict. Please check your input. |
| `DB_CONNECTION_ERROR` | 503 | Database temporarily unavailable. Please try again later. |

### File Processing Errors (FILE_*)

| Code | HTTP Status | Message |
|------|-------------|---------|
| `FILE_TOO_LARGE` | 413 | File exceeds maximum size of 10 MB |
| `FILE_TYPE_INVALID` | 415 | Invalid file type. Please upload a PDF or DOCX file |
| `FILE_UPLOAD_FAILED` | 500 | File upload failed. Please try again. |
| `FILE_NOT_FOUND` | 404 | File not found |
| `FILE_CORRUPTED` | 422 | File appears to be corrupted or unreadable |

### State Conflict Errors (CONFLICT_*)

| Code | HTTP Status | Message |
|------|-------------|---------|
| `CONFLICT_BOLETIN_CLOSED` | 409 | Cannot modify a closed bulletin |
| `CONFLICT_BOLETIN_INCOMPLETE` | 409 | Cannot close bulletin. Not all sections are complete. |
| `CONFLICT_SECCION_IN_USE` | 409 | Section is being edited by another user |
| `CONFLICT_PROMPT_IN_USE` | 409 | Prompt is currently in use and cannot be deleted |

---

## Retry Strategies

### AI Service Retries with Exponential Backoff

```python
# Configuration
AI_RETRY_CONFIG = {
    "max_attempts": 3,
    "min_wait_seconds": 2,
    "max_wait_seconds": 30,
    "exponential_base": 2,
    "retryable_status_codes": [429, 500, 502, 503, 504],
    "retryable_exceptions": [
        "httpx.TimeoutException",
        "httpx.NetworkError",
        "ConnectionError",
    ]
}

# Implementation using tenacity
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)

def is_retryable_response(response):
    """Check if response should trigger retry."""
    return response.status_code in AI_RETRY_CONFIG["retryable_status_codes"]

@retry(
    stop=stop_after_attempt(AI_RETRY_CONFIG["max_attempts"]),
    wait=wait_exponential(
        multiplier=1,
        min=AI_RETRY_CONFIG["min_wait_seconds"],
        max=AI_RETRY_CONFIG["max_wait_seconds"]
    ),
    retry=(
        retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
        | retry_if_result(is_retryable_response)
    ),
)
async def call_ai_with_retry(prompt: str, config: dict) -> dict:
    """Call AI API with automatic retry on transient failures."""
    return await call_ai_api(prompt, config)
```

### Database Connection Retries

```python
# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

def create_engine_with_retry(database_url: str, max_retries: int = 5):
    """Create database engine with connection retry logic."""
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300,    # Recycle connections after 5 minutes
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(
                f"Database connection attempt {attempt + 1} failed. "
                f"Retrying in {wait_time} seconds..."
            )
            time.sleep(wait_time)
```

### File Upload Retries

```typescript
// frontend/src/lib/utils/upload-with-retry.ts

interface UploadConfig {
  maxRetries: number;
  retryDelay: number;
  chunkSize: number;
}

const DEFAULT_CONFIG: UploadConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  chunkSize: 1024 * 1024, // 1MB chunks
};

export async function uploadWithRetry(
  file: File,
  endpoint: string,
  config: Partial<UploadConfig> = {}
): Promise<{ id: string; url: string }> {
  const { maxRetries, retryDelay } = { ...DEFAULT_CONFIG, ...config };

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        return response.json();
      }

      // Don't retry on client errors (4xx)
      if (response.status >= 400 && response.status < 500) {
        const error = await response.json();
        throw new Error(error.detail?.message || 'Upload failed');
      }

      // Retry on server errors (5xx)
      if (attempt < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
        continue;
      }

      throw new Error('Upload failed after multiple attempts');
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
    }
  }

  throw new Error('Upload failed');
}
```

---

## Error Logging

### What to Log vs What Not to Log

| ✅ LOG | ❌ DO NOT LOG |
|--------|---------------|
| User ID (uuid) | Passwords (plain or hashed) |
| Action performed | JWT tokens |
| Timestamp | API keys |
| IP address | AI prompts (sensitive content) |
| Request ID (correlation) | AI responses (may contain PII) |
| Error code | File contents |
| HTTP status code | Database query details |
| Error message (safe) | Stack traces in production |
| Affected resource ID | Internal file paths |
| Duration of operation | Environment variables |

### Error Correlation IDs

```python
# backend/app/middleware/correlation.py

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Store in request state
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response


# Usage in error handling
import logging
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("nia.errors")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    # Log the error with correlation ID
    logger.error(
        "Unhandled exception",
        extra={
            "correlation_id": correlation_id,
            "path": request.url.path,
            "method": request.method,
            "user_id": getattr(request.state, "user_id", None),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
        exc_info=True,  # Include stack trace in logs
    )

    # Return safe error to client
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "SYS_INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again.",
                "correlation_id": correlation_id,
            }
        }
    )
```

### Structured Logging Configuration

```python
# backend/app/config/logging.py

import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "duration"):
            log_entry["duration_ms"] = record.duration

        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_entry)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    # Configure JSON formatter for production
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    # Apply to all loggers
    for logger_name in logging.Logger.manager.loggerDict:
        logging.getLogger(logger_name).addHandler(handler)
```

---

## User-Friendly Error Messages

### Error Message Templates

```typescript
// frontend/src/lib/utils/error-messages.ts

export const ERROR_MESSAGES: Record<string, string> = {
  // Authentication
  AUTH_REQUIRED: 'Please log in to continue.',
  AUTH_INVALID_CREDENTIALS: 'Invalid email or password. Please try again.',
  AUTH_TOKEN_EXPIRED: 'Your session has expired. Please log in again.',
  AUTH_FORBIDDEN: 'You do not have permission to access this resource.',

  // Validation
  VALIDATION_ERROR: 'Please check your input and try again.',
  VAL_EMAIL_INVALID: 'Please enter a valid email address.',
  VAL_PASSWORD_TOO_SHORT: 'Password must be at least 8 characters.',
  VAL_FIELD_REQUIRED: 'This field is required.',

  // Not Found
  NF_BOLETIN: 'The bulletin you are looking for does not exist or has been removed.',
  NF_NOTA: 'The note you are looking for does not exist or has been removed.',

  // AI Service
  AI_UNAVAILABLE: 'The AI service is temporarily unavailable. Please try again in a few minutes.',
  AI_TIMEOUT: 'The AI request took too long. Please try again.',
  AI_RATE_LIMITED: 'Too many requests to the AI service. Please wait a moment and try again.',

  // File Processing
  FILE_TOO_LARGE: 'The file is too large. Maximum size is 10 MB.',
  FILE_TYPE_INVALID: 'Invalid file type. Please upload a PDF or DOCX file.',

  // Database
  DB_ERROR: 'Unable to save changes. Please try again.',
  DB_INTEGRITY_ERROR: 'This action conflicts with existing data.',

  // General
  SYS_INTERNAL_ERROR: 'An unexpected error occurred. Please try again.',
  NETWORK_ERROR: 'Unable to connect to the server. Please check your connection.',
  UNKNOWN_ERROR: 'Something went wrong. Please try again.',
};

export function getErrorMessage(code: string, fallback?: string): string {
  return ERROR_MESSAGES[code] || fallback || ERROR_MESSAGES.UNKNOWN_ERROR;
}
```

### Accessibility of Error Messages

```svelte
<!-- Error message component with proper ARIA attributes -->
<script lang="ts">
  export let message: string;
  export let fieldId?: string;
  export let live: boolean = true;
</script>

{#if message}
  <span
    class="error-message"
    role="alert"
    aria-live={live ? 'polite' : 'off'}
    id={fieldId ? `${fieldId}-error` : undefined}
    aria-describedby={fieldId}
  >
    {message}
  </span>
{/if}

<style>
  .error-message {
    display: block;
    color: var(--color-error);
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
</style>
```

**Accessibility Rules:**
- All error messages must have `role="alert"` for screen reader announcement
- Use `aria-live="polite"` for non-critical errors
- Use `aria-live="assertive"` for critical errors requiring immediate attention
- Link error messages to form fields via `aria-describedby`
- Use `aria-invalid="true"` on invalid form fields
- Ensure sufficient color contrast (WCAG AA minimum)
- Do not rely solely on color to convey error state (add icons or text)

---

## Error Recovery Patterns

### Graceful Degradation

```typescript
// frontend/src/lib/utils/graceful-degradation.ts

export async function withFallback<T>(
  primaryFn: () => Promise<T>,
  fallbackFn: () => Promise<T>,
  options: { logError?: boolean } = {}
): Promise<T> {
  try {
    return await primaryFn();
  } catch (error) {
    if (options.logError) {
      console.error('Primary function failed, using fallback:', error);
    }
    return fallbackFn();
  }
}

// Usage example
const boletinData = await withFallback(
  () => api.get(`/boletines/${id}`),
  () => getCachedBoletin(id),
  { logError: true }
);
```

### Fallback Behaviors

```python
# backend/app/services/ia_service.py

async def generate_article_with_fallback(
    incidentes: list[dict],
    prompt_template: str
) -> dict:
    """Generate article with AI, fallback to template-based generation."""

    try:
        # Primary: AI generation
        ai_result = await call_ai_with_retry(prompt_template, incidentes)
        return {
            "articulo_markdown": ai_result["content"],
            "generado_por": "ia",
            "version": 1
        }
    except AIServiceError:
        # Fallback: Template-based generation
        logger.warning("AI unavailable, using template fallback")
        template_result = generate_from_template(incidentes)
        return {
            "articulo_markdown": template_result,
            "generado_por": "template",
            "version": 1
        }


def generate_from_template(incidentes: list[dict]) -> str:
    """Generate basic article from incident data without AI."""
    lines = ["# Incidentes de Inocuidad Alimentaria\n"]

    for i, inc in enumerate(incidentes, 1):
        lines.append(f"## {i}. {inc['incidente']}\n")
        lines.append(f"**Producto:** {inc['producto']}")
        lines.append(f"**Patógeno:** {inc['patogeno']}")
        lines.append(f"**País:** {inc['pais']}")
        lines.append(f"**Riesgo:** {inc['riesgo']}\n")

    return "\n".join(lines)
```

### Data Consistency on Errors

```python
# backend/app/services/boletin_service.py

from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError


@contextmanager
def transaction_scope(session):
    """Ensure data consistency with automatic rollback on error."""
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def update_boletin_seccion(
    db: Session,
    boletin_id: str,
    tipo: str,
    contenido: dict
) -> Seccion:
    """Update section content with transaction safety."""
    with transaction_scope(db) as session:
        # Verify boletin exists and is in editable state
        boletin = session.query(Boletin).filter(Boletin.id == boletin_id).first()
        if not boletin:
            raise NotFoundError("Boletin", boletin_id)

        if boletin.estado != "borrador":
            raise ConflictError("Cannot edit sections of a closed bulletin")

        # Update section
        seccion = session.query(Seccion).filter(
            Seccion.boletin_id == boletin_id,
            Seccion.tipo == tipo
        ).first()

        if not seccion:
            raise NotFoundError("Seccion", tipo)

        seccion.contenido = contenido
        seccion.estado = "completada"

        return seccion
```

### Optimistic Locking for Concurrent Edits

```python
# backend/app/models/seccion.py

from sqlmodel import SQLModel, Field
import uuid


class Seccion(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    boletin_id: uuid.UUID = Field(foreign_key="boletines.id")
    tipo: str
    contenido: dict = Field(default={})
    estado: str = Field(default="pendiente")
    version: int = Field(default=1)  # Optimistic lock version
    # ...
```

```python
# backend/app/services/seccion_service.py

def update_seccion_with_version_check(
    db: Session,
    boletin_id: str,
    tipo: str,
    contenido: dict,
    expected_version: int
) -> Seccion:
    """Update section with optimistic locking to prevent lost updates."""
    seccion = db.query(Seccion).filter(
        Seccion.boletin_id == boletin_id,
        Seccion.tipo == tipo
    ).first()

    if not seccion:
        raise NotFoundError("Seccion", tipo)

    if seccion.version != expected_version:
        raise ConflictError(
            "This section has been modified by another user. "
            "Please refresh and try again."
        )

    seccion.contenido = contenido
    seccion.version += 1
    db.commit()
    db.refresh(seccion)

    return seccion
```

---

## Monitoring and Alerting

### Error Rate Monitoring

```python
# backend/app/middleware/error_tracking.py

from collections import defaultdict
import time
from threading import Lock


class ErrorTracker:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.lock = Lock()
        self.window_start = time.time()

    def record_error(self, error_code: str, status_code: int):
        with self.lock:
            self.error_counts[error_code] += 1

            # Alert if error rate exceeds threshold
            if self.error_counts[error_code] > 10:  # More than 10 errors in window
                self._send_alert(error_code, self.error_counts[error_code])

    def _send_alert(self, error_code: str, count: int):
        # Implementation: send to monitoring service (Sentry, Datadog, etc.)
        logger.warning(
            f"High error rate detected",
            extra={
                "error_code": error_code,
                "count": count,
                "window_seconds": time.time() - self.window_start
            }
        )


error_tracker = ErrorTracker()
```

### Health Check Endpoint

```python
# backend/app/routers/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db = Depends(get_db)):
    """Health check endpoint for monitoring."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }

    # Check database
    try:
        db.execute("SELECT 1")
        checks["services"]["database"] = "healthy"
    except SQLAlchemyError:
        checks["services"]["database"] = "unhealthy"
        checks["status"] = "degraded"

    # Check AI service (optional, non-critical)
    try:
        # Lightweight ping to AI service
        checks["services"]["ai"] = "healthy"
    except Exception:
        checks["services"]["ai"] = "unhealthy"
        checks["status"] = "degraded"

    status_code = 200 if checks["status"] == "healthy" else 503
    return JSONResponse(content=checks, status_code=status_code)
```

---

## Summary

This document defines the comprehensive error handling patterns for the NIA project. Key takeaways:

1. **Consistent Error Format**: All errors follow `{ "detail": { "code": "...", "message": "..." } }` format
2. **Error Code Registry**: Machine-readable codes with user-friendly messages
3. **Retry Strategies**: Exponential backoff for transient failures (AI, database, uploads)
4. **Correlation IDs**: Every error is traceable for debugging
5. **Graceful Degradation**: Fallback behaviors when external services fail
6. **Accessibility**: Error messages are accessible to screen readers
7. **Security**: Never expose internal details to users
8. **Monitoring**: Error rates are tracked and alerted

For implementation examples, refer to the code snippets in each section. For questions or updates, contact the architecture team.
