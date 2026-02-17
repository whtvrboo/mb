import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

const globalOptions = {
    stubs: {
        Teleport: true,
        Transition: {
            template: '<div><slot /></div>'
        }
    }
}

describe('Modal', () => {
    it('renders with accessibility attributes when open', async () => {
        const wrapper = mount(Modal, {
            props: {
                modelValue: true,
                title: 'Test Modal',
                closeable: true
            },
            global: globalOptions
        })

        const dialog = wrapper.find('[role="dialog"]')
        expect(dialog.exists()).toBe(true)
        expect(dialog.attributes('aria-modal')).toBe('true')

        // Title ID check
        const title = wrapper.find('h3')
        expect(title.exists()).toBe(true)
        const titleId = title.attributes('id')
        expect(titleId).toBeDefined()
        expect(dialog.attributes('aria-labelledby')).toBe(titleId)

        // Close button label check
        const closeBtn = wrapper.find('button[aria-label="Close modal"]')
        expect(closeBtn.exists()).toBe(true)
    })

    it('closes on escape key press', async () => {
        const wrapper = mount(Modal, {
            props: {
                modelValue: true,
                closeable: true
            },
            global: globalOptions
        })

        // Dispatch escape key event to window since the listener is global
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

        expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
        expect(wrapper.emitted('close')).toBeTruthy()
    })
})
