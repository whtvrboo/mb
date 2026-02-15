## 2024-05-23 - Interactive Loading States
**Learning:** Users lack confidence when critical actions (like "Add Item") provide no immediate feedback during async operations, leading to duplicate submissions or confusion.
**Action:** Always implement a dedicated `isActing` state (e.g., `isAddingItem`) for primary action buttons, replacing the static icon with a spinner and disabling the input to prevent double-submit.
