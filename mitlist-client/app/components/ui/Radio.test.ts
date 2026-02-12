import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders correctly', () => {
    const wrapper = mount(Radio, {
      props: {
        modelValue: '',
        value: 'option1'
      }
    })
    const input = wrapper.find('input[type="radio"]')
    expect(input.exists()).toBe(true)
    expect(input.element.checked).toBe(false)
  })

  it('updates modelValue when clicked', async () => {
    const wrapper = mount(Radio, {
      props: {
        modelValue: '',
        value: 'option1'
      }
    })
    const input = wrapper.find('input[type="radio"]')
    await input.trigger('change')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['option1'])
  })
})
