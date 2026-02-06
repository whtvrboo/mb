## 2026-02-06 - Modal Accessibility & Nuxt Auto-Imports
**Learning:** Nuxt's auto-import logic prefixes components in subdirectories (e.g., `components/ui/Modal.vue` -> `<UiModal />`). Existing pages (like `test-ui.vue`) using `<Modal />` may be broken if aliases aren't configured.
**Action:** When working with UI components, prefer the explicit namespaced name (e.g., `UiModal`) or verify `components.d.ts` resolution. Always add `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` to modals.

## 2026-02-06 - Testing Nuxt Components
**Learning:** Testing dynamic accessibility attributes (like `useId`) in unit tests can be tricky with snapshots. Static analysis of the component file (reading content) is a robust fallback for verifying attribute presence when full mounting is complex or environment-limited.
**Action:** Use static analysis tests for simple attribute verification to avoid test fragility.
