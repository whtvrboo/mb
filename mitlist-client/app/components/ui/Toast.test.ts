import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Toast Accessibility', () => {
  it('has correct ARIA roles and labels', () => {
    const filePath = path.resolve(__dirname, 'Toast.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for dynamic role binding
    expect(content).toContain(':role="role"')

    // Check for close button label
    expect(content).toContain('aria-label="Close notification"')
  })
})
