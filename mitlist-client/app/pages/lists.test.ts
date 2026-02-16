import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListsPage from './lists.vue'

// Mock Nuxt Link component to avoid errors
const NuxtLinkStub = {
  template: '<a><slot /></a>',
  props: ['to']
}

// Mock composables
vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: vi.fn().mockResolvedValue([{ id: 1, name: 'Groceries' }]),
    createList: vi.fn(),
    listItems: vi.fn().mockResolvedValue([]),
    addItem: vi.fn().mockImplementation(() => new Promise(resolve => {
        setTimeout(() => resolve({ id: 99, name: 'Milk', is_checked: false, quantity_value: 1 }), 100)
    })),
    deleteItem: vi.fn(),
    updateItem: vi.fn()
  })
}))

vi.mock('~/composables/useAuth', () => ({
  useAuth: () => ({
    listGroupMembers: vi.fn().mockResolvedValue([]),
    groupId: { value: 1 }
  })
}))

describe('ListsPage', () => {
  it('should show loading state when adding item', async () => {
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          NuxtLink: NuxtLinkStub,
          GroceryListItem: true // Stub child components
        }
      }
    })

    // Wait for initial fetch
    await new Promise(resolve => setTimeout(resolve, 10))
    await wrapper.vm.$nextTick()

    const input = wrapper.find('input[placeholder="Add new item..."]')
    const button = wrapper.find('button[aria-label="Add item"]')

    expect(input.exists()).toBe(true)
    expect(button.exists()).toBe(true)

    // Simulate typing
    await input.setValue('Milk')

    // Click Add
    await button.trigger('click')

    // Check loading state immediately after click
    expect(wrapper.find('button[aria-busy="true"]').exists()).toBe(true)
    expect(wrapper.find('svg.animate-spin').exists()).toBe(true)
    // Icon should NOT be present in the button
    expect(button.find('.material-symbols-outlined').exists()).toBe(false)

    // Wait for add to complete (mock delay is 100ms)
    await new Promise(resolve => setTimeout(resolve, 150))
    await wrapper.vm.$nextTick()

    // Check loading state gone
    expect(wrapper.find('button[aria-busy="true"]').exists()).toBe(false)
    expect(wrapper.find('svg.animate-spin').exists()).toBe(false)

    // Check if icon is back
    const addButton = wrapper.find('button[aria-label="Add item"]')
    expect(addButton.find('.material-symbols-outlined').text()).toBe('add')
  })
})
