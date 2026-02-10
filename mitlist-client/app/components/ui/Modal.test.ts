import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal', () => {
  it('renders with correct accessibility attributes', async () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Test Modal',
        closeable: true
      },
      global: {
        stubs: {
          Teleport: true,
          Transition: true // Stub transition to avoid async rendering issues
        }
      }
    })

    // Find the modal dialog container
    // The structure is: Teleport -> Transition -> div.fixed (overlay) -> div.relative (dialog)
    // Since we stub Teleport and Transition, wrapper.element should be or contain the div.fixed

    // Find the inner dialog div (the one with bg-white)
    const dialog = wrapper.find('.bg-white.border-\\[3px\\]')

    expect(dialog.exists()).toBe(true)

    // Check for role="dialog"
    expect(dialog.attributes('role')).toBe('dialog')

    // Check for aria-modal="true"
    expect(dialog.attributes('aria-modal')).toBe('true')

    // Check for aria-labelledby
    const labelledBy = dialog.attributes('aria-labelledby')
    expect(labelledBy).toBeDefined()

    // Find title and check if it has the same ID
    const title = wrapper.find('h3')
    expect(title.exists()).toBe(true)
    expect(title.attributes('id')).toBe(labelledBy)

    // Check close button aria-label
    const closeButton = wrapper.find('button')
    expect(closeButton.exists()).toBe(true)
    expect(closeButton.attributes('aria-label')).toBe('Close modal')
  })

  it('closes on Escape key press', async () => {
    const wrapper = mount(Modal, {
      props: {
        modelValue: true,
        title: 'Test Modal',
        closeable: true
      },
      global: {
        stubs: {
          Teleport: true,
          Transition: true
        }
      }
    })

    // Simulate Escape key press on window
    await wrapper.trigger('keydown.escape')

    // Check if update:modelValue was emitted with false
    // Since the event listener is likely on window/document, wrapper.trigger might not work directly
    // depending on implementation. But if we use useEventListener on window,
    // we should trigger on window.

    // Triggering on window directly:
    const event = new KeyboardEvent('keydown', { key: 'Escape' })
    window.dispatchEvent(event)

    // Wait for Vue updates
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
