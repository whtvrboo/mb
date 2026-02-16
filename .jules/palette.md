# Palette's Journal

## 2024-02-16 - Static Analysis for Accessibility Testing
**Learning:** In this codebase, complex Nuxt pages with heavy composable dependencies are tested for accessibility features (like `aria-label`, `sr-only` classes) using static analysis (reading file content as string) rather than mounting the component. This avoids the overhead of mocking the entire Nuxt context for simple presence checks.
**Action:** When adding accessibility features to pages, use `fs.readFileSync` in Vitest to verify the markup exists, ensuring the features are present without brittle test setup.
