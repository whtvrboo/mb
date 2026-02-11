import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal Accessibility', () => {
  it('renders with correct ARIA attributes', () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Test Modal',
        closeable: true
      },
      global: {
        stubs: {
          Teleport: true
        }
      }
    })

    const modal = wrapper.find('[role="dialog"]')
    expect(modal.exists()).toBe(true)
    expect(modal.attributes('aria-modal')).toBe('true')

    // Check aria-labelledby
    const titleId = modal.attributes('aria-labelledby')
    expect(titleId).toBeDefined()
    const titleElement = wrapper.find(`#${titleId}`)
    expect(titleElement.exists()).toBe(true)
    expect(titleElement.text()).toBe('Test Modal')

    // Check close button label
    const closeButton = wrapper.find('button[aria-label="Close modal"]')
    expect(closeButton.exists()).toBe(true)
  })

  it('emits close on Escape key', async () => {
    const wrapper = mount(Modal, {
        props: {
            modelValue: true,
            closeable: true
        },
        global: {
            stubs: {
                Teleport: true
            }
        },
        attachTo: document.body
    })

    await wrapper.trigger('keydown', { key: 'Escape' })
    // If trigger doesn't bubble to window where listener is attached, we might need manual dispatch
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

    // Wait for event loop
    expect(wrapper.emitted('close')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])

    wrapper.unmount()
  })
})
