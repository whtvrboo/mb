import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('renders with accessible focus styles', () => {
    const wrapper = mount(Checkbox, {
      props: { label: 'Test Checkbox' }
    })
    const input = wrapper.find('input[type="checkbox"]')

    // Check for focus-visible classes
    const classes = input.classes()
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
    expect(classes).toContain('focus-visible:outline-none')
  })

  it('hides decorative icon from screen readers', () => {
    const wrapper = mount(Checkbox, {
      props: { modelValue: true }
    })
    // The icon is inside a span with class material-symbols-outlined
    const icon = wrapper.find('.material-symbols-outlined')
    expect(icon.exists()).toBe(true)
    expect(icon.attributes('aria-hidden')).toBe('true')
  })
})
