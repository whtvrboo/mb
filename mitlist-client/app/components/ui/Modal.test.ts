import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Modal Accessibility', () => {
  it('has correct ARIA roles and labels', () => {
    const filePath = path.resolve(__dirname, 'Modal.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for dialog role and modal attribute
    expect(content).toContain('role="dialog"')
    expect(content).toContain('aria-modal="true"')

    // Check for title labelling
    expect(content).toContain(':aria-labelledby="titleId"')

    // Check for close button label
    expect(content).toContain('aria-label="Close modal"')
  })
})
