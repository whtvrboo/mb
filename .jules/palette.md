## 2025-05-15 - Playwright Verification of Nuxt SSR
**Vulnerability:** N/A (Testing limitation)
**Learning:** Verifying protected routes in Nuxt (SSR) with Playwright network mocks fails because server-side `useFetch` calls bypass the browser network layer.
**Action:** When verifying Nuxt apps without a backend, either temporarily disable SSR (`ssr: false` in `nuxt.config.ts`) or trigger client-side navigation (e.g., `router.push`) from a public page to ensure API requests happen in the browser where Playwright can intercept them.

## 2025-05-15 - Missing Group Context in Tests
**Vulnerability:** N/A (State management)
**Learning:** `useAuth().groupId` relies on `useCurrentGroupId` state, which defaults to `null`. In the real app, this is likely set by a middleware or plugin that was not active or mocked in the test environment, causing features like "Add Item" to be disabled by default.
**Action:** When testing group-dependent features, ensure `current-group-id` state is explicitly initialized in the test setup (e.g., via `useState` mock or `page.evaluate`).
