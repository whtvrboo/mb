import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Alert from './Alert.vue'

describe('Alert', () => {
  it('renders correct role and icon for error variant', () => {
    const wrapper = mount(Alert, {
      props: {
        variant: 'error',
        title: 'Error Title'
      }
    })

    expect(wrapper.attributes('role')).toBe('alert')
    expect(wrapper.text()).toContain('error') // Icon name
    expect(wrapper.text()).toContain('Error Title')
    expect(wrapper.classes()).toContain('border-background-dark')
  })

  it('renders correct role and icon for warning variant', () => {
    const wrapper = mount(Alert, {
      props: {
        variant: 'warning'
      }
    })

    expect(wrapper.attributes('role')).toBe('alert')
    expect(wrapper.text()).toContain('warning') // Icon name
  })

  it('renders correct role and icon for success variant', () => {
    const wrapper = mount(Alert, {
      props: {
        variant: 'success'
      }
    })

    expect(wrapper.attributes('role')).toBe('status')
    expect(wrapper.text()).toContain('check_circle') // Icon name
  })

  it('renders correct role and icon for info variant', () => {
    const wrapper = mount(Alert, {
      props: {
        variant: 'info'
      }
    })

    expect(wrapper.attributes('role')).toBe('status')
    expect(wrapper.text()).toContain('info') // Icon name
  })
})
