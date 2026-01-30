# 📡 Frontend API Contracts & Error Handling

## 1. Response Envelope

We do **NOT** wrap successful responses in `{ data: ... }`. Consume the resource directly.

- _GET /users/1_ -> `{ "id": 1, ... }`
- _GET /users_ -> `[{ "id": 1 }, ...]`

## 2. Error Taxonomy (RFC 7807 Problem Details)

All API errors are expected to return a standardized JSON structure.

```json
{
  "type": "error:business-logic",
  "code": "INSUFFICIENT_FUNDS",
  "detail": "User balance is 50.00 but attempted 100.00",
  "instance": "/expenses/create",
  "trace_id": "abc-123"
}
```

## 3. Standard Data Layer: TanStack Query (Vue)

- **Queries:** Use `useQuery()` and display `isPending / isError` states explicitly.
- **Mutations:** Use `useMutation()` and disable submit actions while pending.
- **Invalidation:** After successful writes, invalidate with `queryClient.invalidateQueries({ queryKey: [...] })`.

## 3. Frontend Handling Rules (By Status)

- **401 Unauthorized:** Clear auth state and send user to re-auth flow (preserve return URL).
- **403 Forbidden:** Show “not allowed” UX; do not retry.
- **404 Not Found:** If navigating to a resource page, show a not-found screen (not a generic toast).
- **409 Conflict:** Treat as stale write. Refetch, then offer merge/retry UX.
- **422 Validation:** Bind field errors to form inputs via Vee-Validate (never show only a generic toast).
- **429 Rate Limited:** Backoff + retry (respect `Retry-After` header if present).
- **5xx / Network Errors:** Show a retry affordance; do not spam retries without user intent.

## 4. Forms: Vee-Validate + Zod

- **Rule:** Form validation is schema-driven (Zod) and rendered via Vee-Validate field errors.
- **Server validation:** If the API returns 422, map those errors into the form so users can fix inputs without guessing.

## 5. Correlation & Debuggability

- **Trace ID Surfacing:** If `trace_id` exists, include it in the user-visible error details (copy-to-clipboard).
- **Request IDs:** Propagate `X-Request-ID` from the client on every request.
