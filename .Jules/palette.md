## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-02-01 - SSR-Safe Form Association
**Learning:** Hardcoded IDs in components can cause duplicates, and random IDs break hydration. `useId()` solves both for `label`-`input` association.
**Action:** Replace `for="email"`/`id="email"` (which might conflict if multiple login forms existed) with `const id = useId()` binding. Essential for accessible, reusable form components in Nuxt.

## 2026-02-01 - Custom Checkbox Pattern
**Learning:** Using `aria-labelledby` on a checkbox pointing to an external text element is valid, but linking multiple label elements to the input's ID (via `for`) is often more robust and prevents "empty label" accessibility issues when the visual checkbox is separated from the text.
**Action:** Use `const id = useId()` and assign `:id="id"` to the input, then use `:for="id"` on both the visual checkbox wrapper and the text label.
