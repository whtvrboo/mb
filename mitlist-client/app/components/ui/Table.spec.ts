import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Table from './Table.vue'

describe('Table.vue', () => {
    const columns = [
        { key: 'name', label: 'Name' },
        { key: 'id', label: 'ID' }
    ]

    it('renders with index keys (baseline behavior: elements are patched)', async () => {
        const rows = [
            { id: 1, name: 'Alice' },
            { id: 2, name: 'Bob' }
        ]

        const wrapper = mount(Table, {
            props: { columns, rows }
        })

        // Get the initial DOM elements
        const rowsWrapper = wrapper.findAll('tbody tr')
        const firstRowEl = rowsWrapper[0].element
        const secondRowEl = rowsWrapper[1].element

        expect(firstRowEl.textContent).toContain('Alice')
        expect(secondRowEl.textContent).toContain('Bob')

        // Swap the rows
        await wrapper.setProps({
            rows: [
                { id: 2, name: 'Bob' },
                { id: 1, name: 'Alice' }
            ]
        })

        const newRowsWrapper = wrapper.findAll('tbody tr')

        // With index keys, the element at index 0 stays at index 0 and gets patched.
        // So strict equality should hold.
        expect(newRowsWrapper[0].element).toBe(firstRowEl)
        expect(newRowsWrapper[1].element).toBe(secondRowEl)

        // But the content should have changed
        expect(newRowsWrapper[0].element.textContent).toContain('Bob')
        expect(newRowsWrapper[1].element.textContent).toContain('Alice')
    })

    it('renders with unique keys (optimized behavior: elements are moved)', async () => {
        const rows = [
            { id: 1, name: 'Alice' },
            { id: 2, name: 'Bob' }
        ]

        const wrapper = mount(Table, {
            props: { columns, rows, rowKey: 'id' }
        })

        // Get the initial DOM elements
        const rowsWrapper = wrapper.findAll('tbody tr')
        const firstRowEl = rowsWrapper[0].element // Alice's element

        expect(firstRowEl.textContent).toContain('Alice')

        // Swap the rows
        await wrapper.setProps({
            rows: [
                { id: 2, name: 'Bob' },
                { id: 1, name: 'Alice' }
            ]
        })

        const newRowsWrapper = wrapper.findAll('tbody tr')

        // With unique keys, the element for Alice (id=1) should have moved to the second position.
        // So the element at index 0 (now Bob) should NOT be the original first element.
        expect(newRowsWrapper[0].element).not.toBe(firstRowEl)

        // The element at index 1 (now Alice) SHOULD be the original first element.
        expect(newRowsWrapper[1].element).toBe(firstRowEl)
    })
})
