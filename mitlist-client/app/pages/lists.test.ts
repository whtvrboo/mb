import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Lists Page Accessibility', () => {
  it('Add Item button has accessible label and loading state', () => {
    // Resolve path relative to project root (mitlist-client)
    const filePath = path.resolve(process.cwd(), 'app/pages/lists.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for aria-label on the button
    expect(content).toContain('aria-label="Add item"')

    // Check for isAdding state definition
    expect(content).toContain('const isAdding = ref(false)')

    // Check for spinner logic
    expect(content).toContain('v-if="!isAdding"')
    expect(content).toContain('v-else')
    expect(content).toContain('animate-spin')

    // Check for sr-only label
    expect(content).toContain('class="sr-only">Add new item</label>')

    // Check for useId usage
    expect(content).toContain('const inputId = useId()')
    expect(content).toContain(':id="inputId"')
    expect(content).toContain(':for="inputId"')
  })
})
