import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Lists Page Accessibility', () => {
  it('has accessible buttons and inputs', () => {
    const filePath = path.resolve(__dirname, 'lists.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for back button label
    expect(content).toContain('aria-label="Back to dashboard"')

    // Check for add item input label
    expect(content).toContain('aria-label="New item name"')

    // Check for add item button label
    expect(content).toContain('aria-label="Add item"')

    // Check for improved empty state
    expect(content).toContain('List is empty. Add an item below!')
  })
})
