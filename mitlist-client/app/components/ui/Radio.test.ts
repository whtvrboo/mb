import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders correctly', () => {
    const wrapper = mount(Radio, {
      props: {
        label: 'Test Radio',
        value: 'option1'
      }
    })
    expect(wrapper.text()).toContain('Test Radio')
  })

  it('has accessible focus styles', () => {
    const wrapper = mount(Radio, {
      props: {
        label: 'Focus Test',
        value: 'option2'
      }
    })
    const input = wrapper.find('input[type="radio"]')

    // Check for focus ring classes
    const classes = input.classes()
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
    expect(classes).toContain('focus:outline-none')
  })
})
