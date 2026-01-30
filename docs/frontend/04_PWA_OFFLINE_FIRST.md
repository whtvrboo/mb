# 📴 Offline-First PWA Architecture (“Elite Stack”)

This repo targets a **local-first PWA**: the app remains usable offline, writes are queued, and server-state refreshes opportunistically.

## 1. The Refined “Elite Stack” for PWA

| Goal               | Package                            | Implementation                                |
| ------------------ | ---------------------------------- | --------------------------------------------- |
| PWA Base           | `@vite-pwa/nuxt`                   | Sets up the Manifest and Service Worker.      |
| Storage            | IndexedDB (via Dexie)              | Stores the actual data on the device disk.    |
| Persistence        | TanStack Persist                   | Connects TanStack Query cache to IndexedDB.   |
| Sync Logic         | VueUse (`useNetwork` / `isOnline`) | Detects when to trigger the “Offline Queue”.  |
| Background Refresh | Service Worker (Workbox)           | Uses stale-while-revalidate to update assets. |

## 2. Data Ownership Model (Critical)

- **Dexie owns “source of truth” device data** for offline-first domains (the stuff users expect to be present offline).
- **TanStack Query owns “server state cache”** and should be treated as a cache + synchronization layer, not the primary database.
- **Offline Queue (“Outbox”) owns pending writes** until confirmed by the server.

Practical split:

- **Dexie tables:** `entities/*`, `outbox/*`, `meta/*`
- **TanStack Query:** server reads + derived server state; persisted for fast cold-start + offline reads where appropriate.

## 3. IndexedDB Storage (Dexie) Rules

- **Schema versioning:** Every breaking change increments Dexie `db.version(n)` and includes an `upgrade()` step if data must be transformed.
- **Indexing:** Never index huge strings/blobs; store them but don’t index them.
- **Transactions:** Multi-table updates that must be consistent run inside a Dexie transaction.

## 4. TanStack Query Persistence (IndexedDB)

TanStack Query v5 supports persistence via a **persister** backed by an `AsyncStorage` interface.

- **Rule:** Persist only what’s safe to keep on-device (no secrets).
- **Rule:** Set explicit retention (`maxAge`) and bump a `buster` when you ship cache-breaking changes.
- **Rule:** Choose conservative `gcTime` so storage doesn’t grow without bound.

Implementation shape:

- Implement an IndexedDB-backed storage adapter (Dexie can back `getItem/setItem/removeItem`).
- Create a persister (TanStack Query’s persister utilities).
- Configure QueryClient default options to use that persister for queries that should persist.

## 5. Connectivity & Offline Queue Flush

Use VueUse connectivity signals to decide when to flush:

- **Signal:** `isOnline` from VueUse (`useNetwork()`).
- **Rule:** The queue flush is edge-triggered (offline → online) and guarded against concurrency (single active flush).
- **Rule:** Flush is retryable and idempotent (client-side and server-side where possible).

## 6. Service Worker Caching Strategy (Assets)

The Service Worker should prioritize reliable offline loading of the **app shell**.

- **Assets (JS/CSS/images/fonts):** Use **stale-while-revalidate**.
- **API calls:** Default to **network-first** (don’t “cache-first” authenticated JSON APIs by accident).
- **Rule:** Treat “offline data correctness” as the job of Dexie + Outbox, not HTTP cache.

Workbox supports both `generateSW` and `injectManifest` approaches; for complex apps prefer `injectManifest` so the SW logic is explicit.
