## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-01 - Semantic Pagination Components
**Learning:** Using generic `<div>` tags for groups of interactive controls like pagination reduces context for screen reader users. Simply adding `aria-label` to buttons is insufficient if the group itself isn't semantically defined. Furthermore, active page indicators need `aria-current="page"` to be accurately announced, as visual styling (like background colors) is ignored by assistive tech.
**Action:** Always wrap pagination controls in a `<nav aria-label="Pagination">` element. Ensure icon-only controls have explicit `aria-label`s with their decorative icons marked `aria-hidden="true"`, and use `aria-current="page"` to programmatically indicate the active item.
