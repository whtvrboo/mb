import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal', () => {
    it('renders with correct accessibility attributes', async () => {
        const wrapper = mount(Modal, {
            props: {
                modelValue: true,
                title: 'Test Modal',
            },
            global: {
                stubs: {
                    Teleport: true,
                    Transition: {
                        template: '<div><slot /></div>'
                    }
                }
            }
        })

        const dialog = wrapper.find('[role="dialog"]')
        expect(dialog.exists()).toBe(true)
        expect(dialog.attributes('aria-modal')).toBe('true')

        const title = wrapper.find('h3')
        expect(title.exists()).toBe(true)
        const titleId = title.attributes('id')
        expect(titleId).toBeDefined()
        expect(dialog.attributes('aria-labelledby')).toBe(titleId)

        const closeButton = wrapper.find('button[aria-label="Close modal"]')
        expect(closeButton.exists()).toBe(true)
    })

    it('emits close event on escape key', async () => {
         const wrapper = mount(Modal, {
            props: {
                modelValue: true,
                title: 'Test Modal',
            },
            global: {
                stubs: {
                    Teleport: true,
                    Transition: {
                         template: '<div><slot /></div>'
                    }
                }
            },
            attachTo: document.body
        })

        await window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

        expect(wrapper.emitted('update:modelValue')).toBeTruthy()
        expect(wrapper.emitted('close')).toBeTruthy()

        wrapper.unmount()
    })
})
