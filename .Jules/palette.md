## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-01 - Focus Visibility for Custom Controls
**Learning:** Custom form controls using `appearance-none` (Checkbox, Radio) strip away all default browser focus indicators, leaving keyboard users without visual context.
**Action:** Always pair `appearance-none` with explicit `focus-visible` styles (e.g., `ring-2`, `ring-offset-2`) that match the design system's focus ring color.
