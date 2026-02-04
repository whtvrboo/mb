## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-01 - Icon-Only Button Accessibility
**Learning:** Several critical action buttons (Back, Add, Search) were implemented as icon-only elements without `aria-label`, making them invisible or confusing to screen reader users. Also, "Search" was implemented as a non-interactive `div`.
**Action:** Always add `aria-label` to icon-only buttons describing the action. Ensure all interactive elements use semantic tags (`<button>`, `<a>`) or have appropriate roles. Hide decorative icons with `aria-hidden="true"`.
