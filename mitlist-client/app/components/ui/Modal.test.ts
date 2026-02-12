import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from './Modal.vue'

describe('Modal.vue', () => {
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
                    Transition: { template: '<div><slot /></div>' }
                }
            }
        })

        // Find the modal content container (the inner part, not just the overlay)
        // We look for role="dialog"
        const modal = wrapper.find('[role="dialog"]')

        // Expectation: role="dialog" should be present
        expect(modal.exists(), 'Modal should have role="dialog"').toBe(true)

        // Expectation: aria-modal="true" should be present
        expect(modal.attributes('aria-modal'), 'Modal should have aria-modal="true"').toBe('true')

        // Expectation: aria-labelledby should be present and point to an ID
        const labelledBy = modal.attributes('aria-labelledby')
        expect(labelledBy, 'Modal should have aria-labelledby').toBeTruthy()

        // Expectation: The title element should have the ID referenced by aria-labelledby
        const title = wrapper.find('h3')
        expect(title.attributes('id'), 'Title should have id matching aria-labelledby').toBe(labelledBy)

        // Expectation: Close button should have aria-label
        const closeButton = wrapper.find('button.ml-auto') // Targeting the close button in header
        expect(closeButton.attributes('aria-label'), 'Close button should have aria-label').toBe('Close modal')
    })

    it('closes on Escape key press', async () => {
        const wrapper = mount(Modal, {
            props: {
                modelValue: true,
                closeable: true
            },
            global: {
                stubs: {
                    Teleport: true,
                    Transition: { template: '<div><slot /></div>' }
                }
            },
            attachTo: document.body
        })

        // Trigger Escape key on window
        const event = new KeyboardEvent('keydown', { key: 'Escape' })
        window.dispatchEvent(event)

        // Expectation: 'update:modelValue' event should be emitted with false
        expect(wrapper.emitted('update:modelValue'), 'Should emit update:modelValue on Escape').toBeTruthy()
        expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])

        wrapper.unmount()
    })
})
