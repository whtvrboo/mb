## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-16 - Async Composable Pattern
**Learning:** Nuxt composables returning `useApi` (wrapper around `useFetch`) return reactive `AsyncData` objects, not Promises resolving to data. Components using `await composable.method()` imperatively will receive the `AsyncData` object instead of the data array, causing silent bugs (e.g., `lists.value.length` being undefined).
**Action:** Strictly use `$api` (wrapper around `$fetch`) for composable methods intended to be called imperatively (e.g., inside click handlers or `onMounted`), ensuring they return a `Promise` that resolves directly to the payload.
