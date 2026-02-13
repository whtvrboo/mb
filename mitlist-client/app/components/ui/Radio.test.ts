import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders with focus-visible styles', () => {
    const wrapper = mount(Radio, {
      props: {
        modelValue: 'a',
        value: 'a'
      }
    })
    const input = wrapper.find('input[type="radio"]')

    // Check for focus-visible styles as required by accessibility standards
    const classes = input.classes()
    expect(classes).toContain('focus-visible:outline-none')
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
  })
})
