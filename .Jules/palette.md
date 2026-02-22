## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-03 - Focus Visibility on Custom Inputs
**Learning:** Using `sr-only` inputs with custom visual replacements (like `div`s) removes the default browser focus ring, making the element inaccessible to keyboard users unless the visual replacement explicitly handles `:focus-visible` or `peer-focus-visible`.
**Action:** Always add `peer-focus-visible:ring-2` (or similar focus styles) to the visual sibling element of any `sr-only` input to ensure keyboard navigability is visually indicated.
