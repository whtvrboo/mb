import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import Modal from './Modal.vue'

describe('Modal.vue', () => {
  it('renders correctly when open', () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Test Modal',
      },
      global: {
        stubs: {
          Teleport: true,
          Transition: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Test Modal')
  })

  it('has correct accessibility attributes', () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Accessible Modal',
      },
      global: {
        stubs: {
          Teleport: true,
          Transition: true,
        },
      },
    })

    const modal = wrapper.find('[role="dialog"]')
    expect(modal.exists()).toBe(true)
    expect(modal.attributes('aria-modal')).toBe('true')

    // Check if aria-labelledby is present and matches the title id
    const labelledBy = modal.attributes('aria-labelledby')
    expect(labelledBy).toBeDefined()

    const title = wrapper.find('h3')
    expect(title.attributes('id')).toBe(labelledBy)
  })

  it('close button has aria-label', () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        closeable: true,
      },
      global: {
        stubs: {
          Teleport: true,
          Transition: true,
        },
      },
    })

    const closeBtn = wrapper.find('button')
    expect(closeBtn.attributes('aria-label')).toBe('Close modal')
  })
})
