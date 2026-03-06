## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2025-02-14 - Interactive Group Semantic Landmarks & States
**Learning:** Beyond basic `aria-label` for icon-only buttons, reusable components that contain interactive groups (like `Pagination.vue`) require specific semantic landmarks and ARIA states for a robust screen reader experience. Using a `<nav aria-label="...">` instead of a generic `<div>` wrapper helps users navigate to it directly. Additionally, active elements within the group need `aria-current="page"` (not just visual styling), and icon spans need `aria-hidden="true"` to prevent raw ligature text (e.g., "chevron_left") from being announced.
**Action:** When reviewing or creating grouped interactive components (like pagination, tabs, or breadcrumbs), explicitly check for a semantic container, `aria-current` on the active item, and explicit `aria-hidden` on purely decorative icon children.
