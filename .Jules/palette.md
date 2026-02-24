## 2026-01-30 - Accessible Checkbox Label Pattern
**Learning:** When visual design requires separating the input and label text (e.g., in a complex flex layout), wrapping them in a `<label>` isn't always feasible or semantic if it includes non-label content.
**Action:** Use Vue 3.5's `useId()` to generate a unique ID for the label text element and link it to the input via `aria-labelledby`. This maintains accessibility without compromising the visual layout.

## 2026-01-31 - Secure ID Generation
**Learning:** Using `Math.random()` for ID generation causes hydration mismatches in Nuxt/SSR applications and potential ID collisions.
**Action:** Replace all instances of `Math.random()` with Vue 3.5's `useId()` composable for stable, unique, and accessible ID generation.

## 2026-02-01 - Disabled UI vs. Missing Data
**Learning:** In list views (like `lists.vue`), if the parent context (e.g., `groupId`) is missing, the initial data fetch is skipped silently, leaving derived state (e.g., `currentListId`) null. This causes UI elements (like "Add Item") to remain disabled indefinitely without clear feedback to the user or developer, masquerading as a loading state.
**Action:** When UI elements depend on data fetching success, ensure there is a distinct "error" or "empty" state (e.g., "Select a group to view lists") rather than just disabling inputs, to aid debugging and user understanding.
