import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Lists Page Accessibility', () => {
  it('has accessible input and button for adding items', () => {
    // In ESM, process.cwd() is the root of the project (mitlist-client)
    // assuming test is run from mitlist-client directory
    const filePath = path.resolve(process.cwd(), 'app/pages/lists.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for sr-only label
    expect(content).toContain('<label for="new-item-input" class="sr-only">New item name</label>')
    expect(content).toContain('id="new-item-input"')

    // Check for button aria-label
    expect(content).toContain('aria-label="Add item"')

    // Check for loading state usage
    expect(content).toContain('const isAdding = ref(false)')
    // We check for the disabled binding partially to be flexible with whitespace
    expect(content).toContain(':disabled="isLoading || !currentListId || isAdding"')

    // Check for spinner
    expect(content).toContain('v-if="isAdding"')
    expect(content).toContain('animate-spin')
  })
})
