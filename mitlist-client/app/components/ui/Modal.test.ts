import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal Accessibility', () => {
  const stubs = {
    Teleport: true,
    Transition: { template: '<div><slot /></div>' }
  }

  it('renders with role="dialog" and aria-modal="true"', () => {
    const wrapper = mount(Modal, {
      props: { modelValue: true, title: 'Test Modal' },
      global: { stubs }
    })

    // We expect the inner container (or a container within Teleport) to have these roles
    // The Modal uses Teleport to body. Since we stub Teleport, it renders in place.
    const dialog = wrapper.find('[role="dialog"]')
    expect(dialog.exists()).toBe(true)
    expect(dialog.attributes('aria-modal')).toBe('true')
  })

  it('associates title with aria-labelledby', () => {
    const wrapper = mount(Modal, {
      props: { modelValue: true, title: 'My Modal Title' },
      global: { stubs }
    })

    const dialog = wrapper.find('[role="dialog"]')
    const title = wrapper.find('h3') // Assuming h3 is used for title based on reading Modal.vue

    expect(title.exists()).toBe(true)
    const titleId = title.attributes('id')
    expect(titleId).toBeDefined()
    expect(dialog.attributes('aria-labelledby')).toBe(titleId)
  })

  it('close button has aria-label', () => {
    const wrapper = mount(Modal, {
      props: { modelValue: true, closeable: true },
      global: { stubs }
    })

    const closeButton = wrapper.find('button[aria-label="Close"]')
    expect(closeButton.exists()).toBe(true)
  })

  it('closes on Escape key press', async () => {
    const wrapper = mount(Modal, {
      props: { modelValue: true, closeable: true },
      global: { stubs },
      attachTo: document.body
    })

    // Create and dispatch the keyboard event on window
    const event = new KeyboardEvent('keydown', { key: 'Escape' })
    window.dispatchEvent(event)

    // Verify emission
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
    expect(wrapper.emitted('close')).toBeTruthy()

    wrapper.unmount()
  })

  it('cleans up event listener on unmount', () => {
    const addSpy = vi.spyOn(window, 'addEventListener')
    const removeSpy = vi.spyOn(window, 'removeEventListener')

    const wrapper = mount(Modal, {
      props: { modelValue: true },
      global: { stubs }
    })

    expect(addSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

    wrapper.unmount()

    expect(removeSpy).toHaveBeenCalledWith('keydown', expect.any(Function))
  })
})
