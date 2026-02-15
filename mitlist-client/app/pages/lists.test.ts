import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('lists.vue UX Improvements', () => {
  const filePath = path.resolve(process.cwd(), 'app/pages/lists.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  it('contains isAdding state', () => {
    expect(content).toContain('const isAdding = ref(false)')
  })

  it('handleAddItem manages loading state', () => {
    expect(content).toContain('isAdding.value = true')
    expect(content).toContain('try {')
    expect(content).toContain('finally {')
    expect(content).toContain('isAdding.value = false')
  })

  it('input has accessible label and disabled state', () => {
    expect(content).toContain('<label for="new-item-input" class="sr-only">Add new item</label>')
    expect(content).toContain('id="new-item-input"')
    // Check for disabled binding including isAdding
    expect(content).toMatch(/:disabled=".*isAdding.*"/)
  })

  it('add button has aria-label and loading spinner', () => {
    expect(content).toContain('aria-label="Add item"')
    // Check for conditional spinner
    expect(content).toContain('<svg v-if="isAdding"')
    expect(content).toContain('class="animate-spin')
    expect(content).toContain('<span v-else class="material-symbols-outlined')
  })

  it('back button has aria-label', () => {
    expect(content).toContain('<NuxtLink to="/" aria-label="Go back"')
  })
})
