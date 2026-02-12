import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('renders correctly', () => {
    const wrapper = mount(Checkbox, {
      props: {
        modelValue: false
      }
    })
    const input = wrapper.find('input[type="checkbox"]')
    expect(input.exists()).toBe(true)
    expect(input.element.checked).toBe(false)
  })

  it('updates modelValue when clicked', async () => {
    const wrapper = mount(Checkbox, {
      props: {
        modelValue: false
      }
    })
    const input = wrapper.find('input[type="checkbox"]')
    await input.setValue(true)
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([true])
  })
})
