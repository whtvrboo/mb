import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('GroceryListItem Accessibility', () => {
  it('delete button has focus-visible styles', () => {
    const filePath = path.resolve(__dirname, 'GroceryListItem.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for focus-visible:opacity-100 to ensure button becomes visible on focus
    expect(content).toContain('focus-visible:opacity-100')

    // Check for focus ring to ensure focus state is clear
    expect(content).toContain('focus-visible:ring-2')
  })

  it('wraps content in label for hit area expansion', () => {
    const filePath = path.resolve(__dirname, 'GroceryListItem.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for the label with cursor-pointer wrapping the content
    expect(content).toContain('<label class="flex items-start gap-3 flex-1 cursor-pointer select-none group/label">')
  })
})
