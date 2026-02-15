import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Checkbox from './Checkbox.vue'

describe('Checkbox', () => {
    it('has accessible focus styles', () => {
        const wrapper = mount(Checkbox, {
            props: {
                label: 'Test Checkbox',
                modelValue: false
            }
        })

        const input = wrapper.find('input[type="checkbox"]')

        // These are the classes we expect to see for proper keyboard accessibility
        const classes = input.classes()
        expect(classes).toContain('focus-visible:ring-2')
        expect(classes).toContain('focus-visible:ring-offset-2')
        expect(classes).toContain('focus-visible:ring-background-dark')
        expect(classes).toContain('focus-visible:outline-none')
    })
})
