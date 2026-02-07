import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('has accessible focus styles', () => {
    const wrapper = mount(Checkbox, {
      props: {
        modelValue: false
      }
    })
    const input = wrapper.find('input[type="checkbox"]')

    // Check for focus-visible ring classes which are essential for keyboard a11y
    expect(input.classes()).toContain('focus-visible:ring-2')
    expect(input.classes()).toContain('focus-visible:ring-background-dark')
    expect(input.classes()).toContain('focus-visible:ring-offset-2')
    expect(input.classes()).toContain('focus:outline-none')
  })
})
