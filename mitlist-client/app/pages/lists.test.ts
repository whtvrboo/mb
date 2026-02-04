import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Lists Page Accessibility', () => {
  it('has accessible buttons and inputs', () => {
    const filePath = path.resolve(__dirname, 'lists.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for ARIA label on Back button
    expect(content).toContain('aria-label="Go back"')

    // Check for ARIA label on Add button
    expect(content).toContain('aria-label="Add item"')

    // Check for ARIA label on Input
    expect(content).toContain('aria-label="New item name"')

    // Check for alt text on Avatar image
    // We expect a dynamic binding or static text
    expect(content).toMatch(/:alt="[^"]*"|alt="[^"]*"/)
  })
})
