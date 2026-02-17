import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders with focus-visible styles', () => {
    const wrapper = mount(Radio)
    const input = wrapper.find('input[type="radio"]')

    expect(input.classes()).toContain('focus-visible:outline-none')
    expect(input.classes()).toContain('focus-visible:ring-2')
    expect(input.classes()).toContain('focus-visible:ring-offset-2')
    expect(input.classes()).toContain('focus-visible:ring-background-dark')
  })
})
