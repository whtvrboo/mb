
## 2025-02-28 - Missing ARIA Labels on Icon-only Buttons
**Learning:** The application frequently uses raw `<button>` elements with nested `<span class="material-symbols-outlined">` icons for actions like editing, deleting, or revealing secrets (e.g., in `pets.vue`, `finance.vue`, `documents.vue`). These lack inherent accessible names, making them unreadable to screen readers.
**Action:** When auditing pages or creating new components, always verify that icon-only interactive elements explicitly define an `aria-label` attribute describing the action.
