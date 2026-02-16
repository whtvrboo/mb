import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

describe('GroceryListItem Accessibility', () => {
  it('delete button has focus-visible styles', () => {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.resolve(__dirname, 'GroceryListItem.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for focus-visible:opacity-100 to ensure button becomes visible on focus
    expect(content).toContain('focus-visible:opacity-100')

    // Check for focus ring to ensure focus state is clear
    expect(content).toContain('focus-visible:ring-2')
  })

  it('entire item row is clickable via label wrapper', () => {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.resolve(__dirname, 'GroceryListItem.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Verify the main container is a label with pointer cursor
    expect(content).toContain('<label class="flex items-start gap-3 flex-1 cursor-pointer">')

    // Verify the inner checkbox container is a div (not a nested label)
    expect(content).toContain('<div class="relative mt-1 shrink-0">')
  })
})
