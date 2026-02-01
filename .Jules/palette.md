## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2025-05-21 - Stable IDs for Form Inputs
**Learning:** Vue 3.5's `useId()` composable provides a robust way to generate unique, hydration-safe IDs for form inputs. This eliminates the risk of duplicate IDs that can break accessibility associations (label-to-input) in Nuxt SSR applications.
**Action:** Replace hardcoded or random IDs with `useId()` when linking `<label>` `for` and `<input>` `id`.
