import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal Accessibility', () => {
  it('renders with correct ARIA attributes when open', () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Accessibility Test'
      },
      global: {
        stubs: {
          Teleport: true // Render content in-place for testing
        }
      }
    })

    // Find the modal container (the one with the white background and border)
    // Based on the component, it's the inner div inside the overlay
    const modalContainer = wrapper.find('[role="dialog"]')

    expect(modalContainer.exists()).toBe(true)
    expect(modalContainer.attributes('aria-modal')).toBe('true')

    // Check aria-labelledby
    const labelledBy = modalContainer.attributes('aria-labelledby')
    expect(labelledBy).toBeDefined()

    // Check title ID matches
    const title = wrapper.find('h3')
    expect(title.attributes('id')).toBe(labelledBy)
  })

  it('renders close button with aria-label', () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        closeable: true
      },
      global: {
        stubs: {
          Teleport: true
        }
      }
    })

    const closeButton = wrapper.find('button[aria-label="Close modal"]')
    expect(closeButton.exists()).toBe(true)
  })
})
