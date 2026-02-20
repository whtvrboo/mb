# Palette's Journal

## 2025-05-20 - Static Analysis for UX Testing
**Learning:** When full component mounting is difficult due to complex environment dependencies (like `nuxt-auth-utils`), `fs` based static analysis in Vitest is a powerful way to enforce UX rules (like `aria-label` presence or specific class usage).
**Action:** Use `fs.readFileSync` + `expect(content).toContain(...)` to verify critical a11y attributes in `.vue` files without needing a running browser or mocked context.

## 2025-05-20 - Shared State in v-for Loops
**Learning:** Using a single `ref(boolean)` with `v-model` inside a `v-for` loop causes all items to share state. This is a common anti-pattern in list components.
**Prevention:** Always use `Set<ID>` or `Map<ID, State>` to track individual item states in lists.
