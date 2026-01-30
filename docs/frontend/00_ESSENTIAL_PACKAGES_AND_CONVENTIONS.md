# 🧰 Frontend Essential Packages & Conventions

These packages are **standard** for frontend work in this repo. If you need an exception, document it in the PR.

## 1. Server State & Networking: TanStack Query (Vue)

- **Package:** `@tanstack/vue-query`
- **Rule:** Server state lives in TanStack Query, not ad-hoc global stores.
- **Musts:**
  - Use stable `queryKey`s.
  - Use `useMutation()` for writes and invalidate/refetch via `queryClient.invalidateQueries()`.
  - Support cancellation by honoring `AbortSignal` in fetches where applicable.

## 2. UI Primitives: Radix Vue

- **Package:** Radix Vue
- **Rule:** Accessible primitives are built from Radix Vue components, then styled via Tailwind.
- **Composition rule:** When wrapping primitives with your own components, you MUST forward props/attrs and events so the accessibility/behavior wiring is preserved.

## 3. Styling: Tailwind CSS

- **Package:** Tailwind
- **Rule:** Tailwind is the default styling system; avoid bespoke one-off CSS unless there’s a clear win.

## 4. Motion & Delight

- **Animation:** `motion.dev`
- **Toasts:** Vue Sonner
- **Confetti:** `canvas-confetti`
- **Hand-drawn visuals:** Rough.js
- **Rules:**
  - Respect reduced-motion preferences for any non-essential animation.
  - Keep “delight” effects behind explicit user action and/or feature flags; never block critical flows.

## 5. Forms: Vee-Validate + Zod

- **Packages:** `vee-validate`, `zod`
- **Rule:** Forms use Vee-Validate; schemas are defined in Zod.
- **Musts:**
  - Field-level errors bind to inputs (not only toasts).
  - API 422 errors map into the form (don’t drop server-side validation).

## 6. Icons: Lucide Vue

- **Package:** Lucide Vue
- **Rule:** Use Lucide icons for consistent iconography. Avoid mixing icon packs.

## 7. PWA / Offline-First (“Elite Stack”)

- **PWA base:** `@vite-pwa/nuxt` (manifest + service worker)
- **Device storage:** IndexedDB via Dexie
- **Query persistence:** TanStack Query persistence (persist Query cache to IndexedDB)
- **Connectivity:** VueUse (`useNetwork()` / `isOnline`) for offline→online transitions
- **Reference:** See `docs/frontend/04_PWA_OFFLINE_FIRST.md`
