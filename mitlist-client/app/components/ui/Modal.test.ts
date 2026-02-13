import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal', () => {
  const defaultMountOptions = {
    global: {
      stubs: {
        Teleport: true,
        Transition: { template: '<div><slot /></div>' }
      }
    }
  }

  it('renders with correct accessibility attributes', () => {
    const wrapper = mount(Modal, {
      ...defaultMountOptions,
      props: {
        modelValue: true,
        title: 'Test Modal',
      },
    })

    const dialog = wrapper.find('div[role="dialog"]')
    expect(dialog.exists()).toBe(true)
    expect(dialog.attributes('aria-modal')).toBe('true')

    // Check if title is linked via aria-labelledby
    const title = wrapper.find('h3')
    expect(title.exists()).toBe(true)
    const titleId = title.attributes('id')
    expect(titleId).toBeTruthy()
    expect(dialog.attributes('aria-labelledby')).toBe(titleId)
  })

  it('renders close button with aria-label', () => {
    const wrapper = mount(Modal, {
      ...defaultMountOptions,
      props: {
        modelValue: true,
        closeable: true,
      },
    })

    const closeButton = wrapper.find('button[aria-label="Close"]')
    expect(closeButton.exists()).toBe(true)
  })

  it('closes on Escape key press', async () => {
    const wrapper = mount(Modal, {
      ...defaultMountOptions,
      props: {
        modelValue: true,
        closeable: true,
      },
    })

    await wrapper.trigger('keydown.esc') // This might not work if listener is on window

    // If listener is on window, we need to dispatch event on window
    await window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
