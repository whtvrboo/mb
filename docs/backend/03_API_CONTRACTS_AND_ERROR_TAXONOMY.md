# 📡 API Contracts & Error Handling

## 1. Response Envelope

We do **NOT** wrap successful responses in `{ data: ... }`. Return the resource directly.

- _GET /users/1_ -> `{ "id": 1, ... }`
- _GET /users_ -> `[{ "id": 1 }, ...]` (Pagination headers handle metadata).

## 2. Error Taxonomy (RFC 7807 Problem Details)

All errors must return a standardized JSON structure.

```json
{
  "type": "error:business-logic",
  "code": "INSUFFICIENT_FUNDS",
  "detail": "User balance is 50.00 but attempted 100.00",
  "instance": "/expenses/create",
  "trace_id": "abc-123"
}
```
