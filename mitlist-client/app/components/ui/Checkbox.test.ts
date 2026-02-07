import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('renders correctly', () => {
    const wrapper = mount(Checkbox, {
      props: {
        label: 'Test Checkbox',
        modelValue: false
      }
    })
    expect(wrapper.text()).toContain('Test Checkbox')
  })

  it('has focus-visible styles', () => {
    const wrapper = mount(Checkbox, {
      props: {
        label: 'Test Checkbox',
        modelValue: false
      }
    })
    const input = wrapper.find('input')
    const classes = input.classes()
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
    expect(classes).toContain('focus:outline-none')
  })
})
