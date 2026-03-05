## 2024-05-15 - Pagination Component Accessibility
**Learning:** Icon-only navigation buttons and pagination components frequently lack accessible names. Adding semantic `<nav>` elements and appropriate ARIA roles ensures users of assistive technologies can correctly identify and use pagination controls.
**Action:** Always wrap pagination elements in a `<nav aria-label="...">`, use `aria-current="page"` for active indicators, and add `aria-hidden="true"` to decorative icons.
