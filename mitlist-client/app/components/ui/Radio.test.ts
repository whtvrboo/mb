import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('has focus-visible styles for keyboard accessibility', () => {
    const wrapper = mount(Radio, {
      props: {
        value: 'option1',
        modelValue: 'option2'
      }
    })
    const input = wrapper.find('input[type="radio"]')
    const classes = input.classes()

    // We check for the presence of specific focus utility classes
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
    expect(classes).toContain('focus:outline-none')
  })
})
