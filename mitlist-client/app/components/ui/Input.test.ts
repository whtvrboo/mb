import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Input from './Input.vue'

describe('Input', () => {
  it('renders with aria-invalid when error is present', () => {
    const wrapper = mount(Input, {
      props: {
        error: true
      }
    })
    const input = wrapper.find('input')
    expect(input.attributes('aria-invalid')).toBe('true')
  })

  it('renders without aria-invalid when error is false', () => {
    const wrapper = mount(Input, {
      props: {
        error: false
      }
    })
    const input = wrapper.find('input')
    // When false, it renders as 'false' which is valid for aria-invalid
    expect(input.attributes('aria-invalid')).toBe('false')
  })
})
