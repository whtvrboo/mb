import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders with focus-visible styles for keyboard navigation', () => {
    const wrapper = mount(Radio, {
      props: {
        label: 'Test Radio',
        name: 'test-group',
        value: 'option1'
      }
    })
    const input = wrapper.find('input[type="radio"]')

    // Check for focus-visible classes
    const classes = input.attributes('class')
    expect(classes).toContain('focus:outline-none')
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
  })
})
