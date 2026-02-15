import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Radio from './Radio.vue'

describe('Radio', () => {
    it('has accessible focus styles', () => {
        const wrapper = mount(Radio, {
            props: {
                label: 'Test Radio',
                value: 'test'
            }
        })

        const input = wrapper.find('input[type="radio"]')

        // These are the classes we expect to see for proper keyboard accessibility
        const classes = input.classes()
        expect(classes).toContain('focus-visible:ring-2')
        expect(classes).toContain('focus-visible:ring-offset-2')
        expect(classes).toContain('focus-visible:ring-background-dark')
        expect(classes).toContain('focus-visible:outline-none')
    })
})
