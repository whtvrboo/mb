import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
  it('renders with accessible focus styles', () => {
    const wrapper = mount(Radio, {
      props: { label: 'Test Radio', value: 'test' }
    })
    const input = wrapper.find('input[type="radio"]')

    const classes = input.classes()
    expect(classes).toContain('focus-visible:ring-2')
    expect(classes).toContain('focus-visible:ring-offset-2')
    expect(classes).toContain('focus-visible:ring-background-dark')
    expect(classes).toContain('focus-visible:outline-none')
  })

  it('hides decorative inner dot from screen readers', () => {
    const wrapper = mount(Radio, {
        props: { modelValue: 'test', value: 'test' }
    })
    // The inner dot is a div following the input
    // <div class="absolute size-3 ...">
    const dot = wrapper.find('.absolute.size-3')
    expect(dot.exists()).toBe(true)
    expect(dot.attributes('aria-hidden')).toBe('true')
  })
})
