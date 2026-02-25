## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-01 - AsyncData Unwrapping
**Learning:** Assigning the result of `useApi` (which returns `AsyncData`) directly to a reactive `ref` expecting the raw data type (e.g., `items.value = await listItems()`) leads to type errors and runtime failures because `AsyncData` wraps the response in `{ data, pending, error }`.
**Action:** Always destructure the response: `const { data } = await listItems()` and assign the value: `items.value = data.value || []`.
