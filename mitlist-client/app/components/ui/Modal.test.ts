import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal Accessibility', () => {
  const defaultOptions = {
    props: {
      modelValue: true,
      title: 'Test Modal'
    },
    global: {
      stubs: {
        Teleport: true,
        Transition: {
          template: '<div><slot /></div>'
        }
      }
    }
  }

  it('renders with role="dialog" and aria-modal="true"', () => {
    const wrapper = mount(Modal, defaultOptions)
    // Attempt to find the main modal container which should have role="dialog"
    // Currently this will fail as the role is not yet added
    const modal = wrapper.find('[role="dialog"]')

    expect(modal.exists()).toBe(true)
    expect(modal.attributes('aria-modal')).toBe('true')
  })

  it('links title with aria-labelledby', () => {
    const wrapper = mount(Modal, defaultOptions)
    // This will fail initially
    const modal = wrapper.find('[role="dialog"]')
    const title = wrapper.find('h3')

    expect(title.exists()).toBe(true)
    const titleId = title.attributes('id')
    expect(titleId).toBeTruthy()
    expect(modal.attributes('aria-labelledby')).toBe(titleId)
  })

  it('close button has aria-label', () => {
    const wrapper = mount(Modal, {
      ...defaultOptions,
      props: {
        ...defaultOptions.props,
        closeable: true
      }
    })

    // The close button is in the header
    const closeBtn = wrapper.find('button.ml-auto')
    expect(closeBtn.exists()).toBe(true)
    expect(closeBtn.attributes('aria-label')).toBe('Close')
  })

  it('emits close event on escape key', async () => {
    const wrapper = mount(Modal, defaultOptions)

    // Dispatch Escape key event to window
    const event = new KeyboardEvent('keydown', { key: 'Escape' })
    window.dispatchEvent(event)

    await wrapper.vm.$nextTick()

    // This will fail initially as there is no listener
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
  })
})
