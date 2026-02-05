## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-14 - Accessible Custom Checkboxes
**Learning:** Custom form controls (like checkboxes built with `div`s) hidden with `.sr-only` must explicitly implement focus styles on the visible sibling using `peer-focus-visible`.
**Action:** Use `peer-focus-visible:ring-2 peer-focus-visible:ring-offset-2 peer-focus-visible:ring-background-dark` on the visible element to ensure keyboard users can see their focus state.
