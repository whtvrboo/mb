import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('renders with focus-visible styles for keyboard navigation', () => {
    const wrapper = mount(Checkbox, {
      props: {
        label: 'Test Checkbox'
      }
    })
    const input = wrapper.find('input[type="checkbox"]')

    // Check for focus-visible classes
    const classes = input.attributes('class')
    expect(classes).toContain('focus:outline-none')
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
  })
})
