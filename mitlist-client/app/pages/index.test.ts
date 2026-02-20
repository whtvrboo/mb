import { describe, it, expect } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'

describe('Dashboard (index.vue) UX & A11y', () => {
  const filePath = path.resolve(__dirname, 'index.vue')
  const content = fs.readFileSync(filePath, 'utf-8')

  it('uses accessible aria-labels for chore completion', () => {
    // Check for dynamic aria-label
    expect(content).toContain(':aria-label="\'Mark \' + chore.chore.name + \' as done\'"')
  })

  it('provides visual feedback for completion (green background)', () => {
    // Check for bg-green-500 instead of bg-sage
    expect(content).not.toContain('bg-sage')
    expect(content).toContain('bg-green-500')
  })

  it('shows loading spinner when completing', () => {
    // Check for spinner SVG or class
    expect(content).toContain('animate-spin')
    expect(content).toContain('completingChores.has(chore.id)')
  })
})
