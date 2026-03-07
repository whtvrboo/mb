## 2024-05-24 - [Add ARIA labels to icon-only buttons]
**Learning:** Found a common pattern in the application's neobrutalism UI where many icon-only buttons (`button` or `NuxtLink` wrapping a `<span class="material-symbols-outlined">`) lack proper accessible names and `aria-hidden="true"` attributes. This degrades the screen reader experience.
**Action:** When adding new UI elements, always ensure icon-only interactable elements have an explicit `aria-label` matching their functionality and add `aria-hidden="true"` on the underlying decorative `span`.
