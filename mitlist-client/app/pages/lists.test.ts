import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Lists Page UX Enhancements', () => {
  it('implements loading state for item creation', () => {
    const filePath = path.resolve(process.cwd(), 'app/pages/lists.vue')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Check for isAdding ref
    expect(content).toContain('const isAdding = ref(false)')

    // Check for isAdding usage in disabled states
    expect(content).toContain(':disabled="isLoading || !currentListId || isAdding"')

    // Check for isAdding usage in button icon
    expect(content).toContain('v-if="!isAdding"')
    expect(content).toContain('v-else class="animate-spin')

    // Check for aria-label
    expect(content).toContain('aria-label="Add item"')
  })
})
