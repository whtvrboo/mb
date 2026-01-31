import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Input from './Input.vue'

describe('Input', () => {
  it('renders with auto-generated id', () => {
    const wrapper = mount(Input)
    expect(wrapper.attributes('id')).toBeDefined()
  })

  it('uses provided id', () => {
    const wrapper = mount(Input, {
      props: { id: 'test-id' }
    })
    expect(wrapper.attributes('id')).toBe('test-id')
  })

  it('sets aria-invalid when error prop is true', () => {
    const wrapper = mount(Input, {
      props: { error: true }
    })
    expect(wrapper.attributes('aria-invalid')).toBe('true')
  })

  it('sets aria-required when required prop is true', () => {
    const wrapper = mount(Input, {
      props: { required: true }
    })
    expect(wrapper.attributes('aria-required')).toBe('true')
  })
})
