## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-02-01 - Stable IDs for SSR
**Learning:** Generating IDs with `Math.random()` causes hydration mismatches in Nuxt applications, breaking accessibility associations (like `for`/`id` or `aria-labelledby`) between server and client.
**Action:** Use Vue 3.5's `useId()` composable to generate stable, unique IDs. This ensures accessible forms work correctly in SSR environments without hydration errors.
