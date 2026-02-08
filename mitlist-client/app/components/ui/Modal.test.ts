import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

describe('Modal Accessibility', () => {
  it('has correct ARIA attributes and event handlers', () => {
    const filePath = path.resolve(__dirname, 'Modal.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for role="dialog"
    expect(content).toContain('role="dialog"')

    // Check for aria-modal="true"
    expect(content).toContain('aria-modal="true"')

    // Check for aria-labelledby
    expect(content).toContain(':aria-labelledby="titleId"')

    // Check for aria-label on close button
    expect(content).toContain('aria-label="Close"')

    // Check for useId import
    expect(content).toContain('useId')

    // Check for Escape key handling
    expect(content).toContain("e.key === 'Escape'")

    // Check for focus management
    expect(content).toContain('tabindex="-1"')
    expect(content).toContain('modalRef.value?.focus()')
  })
})
