import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Lists Page Accessibility', () => {
  it('input has associated label and button has aria-label and loading state', () => {
    // Resolve path relative to current working directory or using process.cwd()
    const filePath = path.resolve(process.cwd(), 'app/pages/lists.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for label association
    expect(content).toContain('<label :for="inputId" class="sr-only">Add new item</label>')
    expect(content).toContain(':id="inputId"')

    // Check for button aria-label
    expect(content).toContain('aria-label="Add item"')

    // Check for loading spinner
    expect(content).toContain('span v-if="isAdding" class="animate-spin')
  })
})
