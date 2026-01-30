# 🧠 UI State Integrity, Concurrency & Performance

## 1. Concurrency Hazards (Stale Responses & Double Submits)

- **Strict Rule:** Any async request that can be re-triggered MUST be safe against reordering.
  - _Example:_ User rapidly changes filters → request A returns after request B.
- **Mitigations (choose at least one):**
  - **Abort Previous:** Cancel in-flight requests when parameters change.
  - **Last-Write-Wins Guard:** Track a monotonically increasing `request_id` and ignore older results.
  - **Keyed Cache/Dedupe:** Requests with the same key share one in-flight promise.
- **Mutation Idempotency:** Any “Create/Submit” action MUST be protected against double-click and refresh retries.
  - _Client:_ Disable button + show pending state.
  - _Server contract:_ Support idempotency keys where feasible.

### Standard Implementation: TanStack Query (Vue)

- **Queries:** Use `useQuery({ queryKey, queryFn })` for server state.
- **Mutations:** Use `useMutation({ mutationFn, onSuccess })` for writes and invalidate with `queryClient.invalidateQueries({ queryKey })`.
- **Cancellation:** When using `fetch`, ensure request cancellation is wired (honor `AbortSignal` when available).

## 2. Optimistic UI & Conflict Handling

- **Optimistic Updates:** Allowed only when you can reliably rollback on failure.
- **Conflict Signals:** Treat `409 Conflict` as “stale write / needs refresh”.
  - _Rule:_ On 409, refetch the resource and present a merge/retry UX (never silently drop user input).
- **Versioned Writes:** If the API exposes `version_id`/ETag, the client MUST send it back on updates.
  - _Goal:_ Detect concurrent edits early and provide explainable UX.

## 3. Performance Anti-Patterns

- **Request Waterfalls:** Do not chain dependent requests in UI effects when a single endpoint can return the needed graph.
- **N+1 Fetching:** No “fetch per row” in lists; use batch endpoints or server-side expansion.
- **Render Thrash:**
  - Avoid global state updates for local UI interactions.
  - Keep derived values memoized when expensive and recomputed on every keystroke.

## 4. Safe UI Migrations (Zero-Drama Rollouts)

- **Forbidden:** Big-bang UI rewrites without feature flags.
- **Required for risky changes:**
  - **Feature Flag / Gradual Rollout**
  - **Backward-Compatible API usage** (support old + new fields during transition)
  - **Telemetry** on error rates and key flows before ramping up
