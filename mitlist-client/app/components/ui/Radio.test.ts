import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders with accessible focus styles', () => {
    const wrapper = mount(Radio, {
      props: {
        label: 'Test Radio',
        value: 'test'
      }
    })
    const input = wrapper.find('input[type="radio"]')

    // Check for focus-visible styles
    expect(input.classes()).toContain('focus-visible:ring-2')
    expect(input.classes()).toContain('focus-visible:ring-offset-2')
    expect(input.classes()).toContain('focus-visible:ring-background-dark')
    expect(input.classes()).toContain('focus-visible:outline-none')
  })
})
