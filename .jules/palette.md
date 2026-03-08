## 2024-03-08 - Semantic Landmarks and Neobrutalist Icon Pagination
**Learning:** For a neobrutalist design system relying on icon-only navigation (like `<span class="material-symbols-outlined">chevron_left</span>`), wrapping interactive collections like pagination in a `<nav aria-label="Pagination">` and explicitly adding `aria-hidden="true"` to the inner icons avoids redundant screen reader babble and establishes a clearer semantic block.
**Action:** Always wrap interactive navigation groups in `<nav>` and strictly mask out decorative ligatures in neobrutalist components.
