# 🧩 Frontend Modular Interoperability Standards

## 1. The Public Interface Rule

Frontend “modules” (Features) are treated as internal packages.

- **Private Implementation:** A feature’s internal components/hooks/utils are PRIVATE.
- **Public Interface:** Each feature exposes an `interface.ts` (and optional `schemas.ts` / `types.ts`).
  - _Allowed:_ Other features may ONLY import from that public surface.
  - _Forbidden:_ Deep imports into another feature’s internal files.

## 2. Shared Code Placement

- **UI Primitives:** Shared, presentation-only components live in `ui/` (no business logic).
- **Domain Logic:** Business rules live in the owning feature module.
- **Cross-Cutting Utilities:** Put truly generic utilities in `shared/` (avoid dumping grounds).

### UI Standardization

- **Accessible primitives:** Use **Radix Vue** for core components (menus, dialogs, popovers, selects, etc.).
- **Styling:** Use **Tailwind** as the default styling system.
- **Icons:** Use **Lucide Vue** (avoid mixing packs).

## 3. Cross-Module Workflows

- **The Problem:** “User accepts invite” triggers “refresh group context” + “seed defaults”.
- **Pattern A (Synchronous/Critical):**
  - Compose in a top-level workflow (route handler / page container / controller hook).
  - _Rule:_ The orchestrator depends on feature interfaces; features do not depend on each other.
- **Pattern B (Asynchronous/Decoupled):**
  - Use an event channel (in-memory pub/sub) for UI-only side effects (toasts, analytics).
  - _Rule:_ No event bus for core correctness; correctness must be explicit in the workflow.

### Composition Rule (Critical)

When wrapping primitives with your own components, you MUST forward props/attrs and event handlers so the underlying accessibility and behavior wiring is preserved.

## 4. Circular Dependencies

- **Strict Ban:** If Feature A imports Feature B, Feature B cannot import Feature A.
- **Resolution:**
  1. Extract shared code into `shared/` or `ui/`.
  2. Dependency injection (pass adapters/functions as arguments).
  3. Event-based coupling for non-critical UI effects.
