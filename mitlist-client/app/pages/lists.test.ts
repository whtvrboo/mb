import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListsPage from './lists.vue'

// Mock composables
vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: vi.fn().mockResolvedValue([
      { id: 1, name: 'Groceries', type: 'grocery' }
    ]),
    createList: vi.fn(),
    listItems: vi.fn().mockResolvedValue([
      { id: 1, list_id: 1, name: 'Milk', quantity_value: 1, is_checked: false, added_by_id: 1 },
      { id: 2, list_id: 1, name: 'Eggs', quantity_value: 12, is_checked: false, added_by_id: 2 }
    ]),
    addItem: vi.fn(),
    deleteItem: vi.fn(),
    updateItem: vi.fn()
  })
}))

vi.mock('~/composables/useAuth', () => ({
  useAuth: () => ({
    listGroupMembers: vi.fn().mockResolvedValue([
      { user_id: 1, user: { name: 'Alice', email: 'alice@example.com' } },
      { user_id: 2, user: { name: 'Bob', email: 'bob@example.com' } }
    ]),
    groupId: { value: 1 }
  })
}))

describe('Lists Page Optimization', () => {
  it('correctly maps user IDs to names using the optimization', async () => {
    // Mount the component
    // Note: Since we mock composables, the component should fetch data on mount.
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          NuxtLink: true, // Stub NuxtLink
          GroceryListItem: { // Stub child component to inspect props
            template: '<div class="grocery-item" :data-added-by="addedBy">{{ name }}</div>',
            props: ['name', 'addedBy']
          }
        }
      }
    })

    // Wait for async calls (fetchData onMounted)
    await new Promise(resolve => setTimeout(resolve, 50))
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    // Find the rendered items
    const items = wrapper.findAll('.grocery-item')

    expect(items.length).toBe(2)

    // Check first item (Milk, added by User 1 -> Alice)
    expect(items[0].text()).toBe('Milk')
    expect(items[0].attributes('data-added-by')).toBe('Alice')

    // Check second item (Eggs, added by User 2 -> Bob)
    expect(items[1].text()).toBe('Eggs')
    expect(items[1].attributes('data-added-by')).toBe('Bob')
  })
})
