## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-15 - Testing Strategy: Static Analysis for Nuxt Pages
**Learning:** Fully rendering Nuxt pages with heavy middleware/auth dependencies (like `useAuth`) in a headless environment is brittle and slow. Static analysis via `fs` and Vitest (checking for critical attributes/logic strings) is a reliable alternative for verifying accessibility compliance and basic state logic presence.
**Action:** When component mounting is blocked by environment complexity, use static file assertions to verify HTML structure and logic presence, following the `GroceryListItem.test.ts` pattern.
