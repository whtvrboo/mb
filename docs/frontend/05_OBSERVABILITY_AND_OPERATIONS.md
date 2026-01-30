# 👁️ Frontend Observability, Logging & Operations

## 1. Error Capture & Guardrails

- **Global Boundary:** Use a top-level error boundary for render-time failures.
- **Unhandled Errors:** Capture `window.onerror` and `unhandledrejection`.
- **User Context:** Attach `user_id`, `group_id` (if applicable), and app `release`/`version` to reports.

## 2. Client Logging (Structured)

- **Rule:** No `console.log` in production builds.
- **Levels:**
  - `INFO`: Key UX events (Invite Accepted).
  - `WARNING`: Recoverable issues (Request retry, stale data).
  - `ERROR`: Unhandled exceptions, failed critical writes.

## 3. Tracing & Correlation

- **Request Correlation:** Generate/forward `X-Request-ID` on every API call.
- **Trace Stitching:** If backend returns `trace_id`, attach it to client error events and UX toasts.
- **Goal:** Reconstruct “click → network → backend trace → DB” for a single user action.

## 4. Performance Monitoring

- **Core UX Metrics:** Track page load and interaction latency (Web Vitals / equivalent).
- **Network Metrics:** Measure API latency and error rates by endpoint + release.
- **Source Maps:** Required for minified stack traces in production.

## 5. Releases & Rollbacks

- **Release Tagging:** Every build MUST include a `release` identifier (git SHA or semver).
- **Feature Flags:** Use for high-risk UX changes; instrument flag cohorts to compare error rates.

## 6. UX Notifications & Motion

- **Toasts:** Use Vue Sonner for user-facing notifications.
  - _Rule:_ Prefer toasts for non-blocking info; use inline errors for forms and blocking failures.
- **Motion:** Use `motion.dev` for animation.
  - _Rule:_ Respect reduced-motion preferences; never animate critical navigation in a way that hides state changes.
- **Delight effects:** `canvas-confetti` and Rough.js are allowed for celebratory/illustrative moments.
  - _Rule:_ Must be lightweight and never run on hot paths (lists, scrolling, typing).
