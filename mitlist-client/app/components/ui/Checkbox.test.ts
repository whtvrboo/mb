import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('renders with focus-visible styles', () => {
    const wrapper = mount(Checkbox)
    const input = wrapper.find('input[type="checkbox"]')

    expect(input.classes()).toContain('focus-visible:outline-none')
    expect(input.classes()).toContain('focus-visible:ring-2')
    expect(input.classes()).toContain('focus-visible:ring-offset-2')
    expect(input.classes()).toContain('focus-visible:ring-background-dark')
  })
})
