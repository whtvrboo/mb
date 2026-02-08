import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import Modal from './Modal.vue'

describe('Modal.vue', () => {
  it('renders with accessibility attributes', async () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Test Modal'
      },
      global: {
        stubs: {
          Teleport: true
        }
      }
    })

    // Check for role="dialog"
    const dialog = wrapper.find('[role="dialog"]')
    expect(dialog.exists(), 'Modal should have role="dialog"').toBe(true)

    // Check for aria-modal="true"
    expect(dialog.attributes('aria-modal'), 'Modal should have aria-modal="true"').toBe('true')

    // Check aria-labelledby
    const labelledBy = dialog.attributes('aria-labelledby')
    expect(labelledBy, 'Modal should have aria-labelledby').toBeTruthy()

    // Check if the title has the same ID
    const title = wrapper.find('h3')
    expect(title.attributes('id'), 'Title should have id matching aria-labelledby').toBe(labelledBy)

    // Check close button aria-label
    // The close button is identified by its class or icon
    const closeBtn = wrapper.find('button.ml-auto')
    expect(closeBtn.attributes('aria-label'), 'Close button should have aria-label').toBe('Close modal')
  })

  it('closes on Escape key', async () => {
     const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Test Modal'
      },
      global: {
        stubs: {
          Teleport: true
        }
      },
      attachTo: document.body
    })

    // Simulate Escape key press on window
    const event = new KeyboardEvent('keydown', { key: 'Escape' })
    window.dispatchEvent(event)

    // Verify emit
    expect(wrapper.emitted('update:modelValue'), 'Should emit update:modelValue on Escape').toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
    expect(wrapper.emitted('close'), 'Should emit close on Escape').toBeTruthy()

    wrapper.unmount()
  })
})
