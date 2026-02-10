import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Modal Accessibility', () => {
  it('has correct ARIA roles and labels', () => {
    const filePath = path.resolve(__dirname, 'Modal.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for unique ID generation
    expect(content).toContain('const titleId = useId()')

    // Check for ARIA role and modal attribute
    expect(content).toContain('role="dialog"')
    expect(content).toContain('aria-modal="true"')

    // Check for title association
    expect(content).toContain(':aria-labelledby="title ? titleId : undefined"')
    expect(content).toContain(':id="titleId"')

    // Check for close button label
    expect(content).toContain('aria-label="Close modal"')

    // Check for Escape key handling with native listeners
    expect(content).toContain("window.addEventListener('keydown', onKeydown)")
    expect(content).toContain("window.removeEventListener('keydown', onKeydown)")
    expect(content).toContain("if (e.key === 'Escape' && props.modelValue) {")
  })
})
