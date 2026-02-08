## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-01 - Neo-brutalist Alert Accessibility
**Learning:** Generic alerts (`role="alert"` or `role="status"`) without distinct visual cues are often missed or confusing. The Neo-brutalist design (hard borders, shadows) requires specific utility classes (`border-[3px]`, `shadow-neobrutalism`) to be consistent.
**Action:** When creating alerts or status messages, combine semantic `role` attributes with the project's specific Neo-brutalist utility classes and semantic icons (`material-symbols-outlined`) for maximum clarity and accessibility.
