## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2025-02-19 - Accessible Form Inputs with useId
**Learning:** Hardcoded IDs in form inputs (e.g., login forms) break accessibility if components are reused or hydrated incorrectly. Vue 3.5's `useId()` solves this elegantly.
**Action:** Default to `useId()` for all form input/label pairs to ensure unique, robust association without manual ID management.
