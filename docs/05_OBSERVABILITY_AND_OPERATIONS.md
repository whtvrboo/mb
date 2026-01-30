# 👁️ Observability, Logging & Metrics

## 1. Structured Logging

- **Format:** JSON (Production), Console (Dev).
- **Context:** Every log entry must include `trace_id`, `user_id`, `group_id` (if context exists).
- **Levels:**
  - `INFO`: Business events (Expense Created).
  - `WARNING`: Recoverable errors (Stale Data, Rate Limit).
  - `ERROR`: Unhandled exceptions, 500s.

## 2. Distributed Tracing

- **Instrumentation:** OpenTelemetry.
- **Propogation:** `X-Request-ID` passed from Nginx -> FastAPI -> Celery -> DB (comment).
- **Goal:** Visualize the full latency waterfall of a "Create Expense" request.

## 3. Health Checks

- **Liveness:** `/health/live` (Returns 200 OK instantly). K8s restarts pod if fails.
- **Readiness:** `/health/ready` (Checks DB connection, Redis connection). Load balancer removes from pool if fails.
