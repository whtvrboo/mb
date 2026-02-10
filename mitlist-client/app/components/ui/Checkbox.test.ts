import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
  it('has focus-visible classes for accessibility', () => {
    const wrapper = mount(Checkbox)
    const input = wrapper.find('input')
    const classes = input.classes()

    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
    expect(classes).toContain('focus-visible:outline-none')
  })
})
