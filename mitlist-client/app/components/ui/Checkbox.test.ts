import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('renders with focus styles on input', () => {
    const wrapper = mount(Checkbox, {
      props: {
        modelValue: false
      }
    })
    const input = wrapper.find('input')
    const classes = input.classes()

    // Check for focus classes
    expect(classes).toContain('focus:outline-none')
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
  })
})
