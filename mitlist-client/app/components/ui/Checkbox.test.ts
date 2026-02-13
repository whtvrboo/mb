import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('renders with focus-visible styles', () => {
    const wrapper = mount(Checkbox, {
      props: {
        modelValue: false
      }
    })
    const input = wrapper.find('input[type="checkbox"]')

    // Check for focus-visible styles as required by accessibility standards
    const classes = input.classes()
    expect(classes).toContain('focus-visible:outline-none')
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
  })
})
