## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-15 - Focus Indicators on Custom Controls
**Learning:** When using `appearance-none` to create custom form controls (like checkboxes/radios), browsers remove all default styling including focus indicators, making the control inaccessible to keyboard users.
**Action:** Always explicitly implement `focus-visible` styles (`focus-visible:outline-none focus-visible:ring-2 ...`) when using `appearance-none` to ensure keyboard navigation remains visible.
