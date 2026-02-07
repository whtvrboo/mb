import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders with focus-visible styles', () => {
    const wrapper = mount(Radio, {
      props: {
        value: 'test',
        modelValue: 'other'
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
