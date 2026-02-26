import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ListsPage from './lists.vue'

// Hoist mocks to be accessible inside vi.mock
const mocks = vi.hoisted(() => ({
  listLists: vi.fn(),
  createList: vi.fn(),
  listItems: vi.fn(),
  addItem: vi.fn(),
  deleteItem: vi.fn(),
  updateItem: vi.fn(),
  listGroupMembers: vi.fn(),
}))

vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: mocks.listLists,
    createList: mocks.createList,
    listItems: mocks.listItems,
    addItem: mocks.addItem,
    deleteItem: mocks.deleteItem,
    updateItem: mocks.updateItem,
  })
}))

vi.mock('~/composables/useAuth', async () => {
  const { ref } = await import('vue')
  return {
    useAuth: () => ({
      listGroupMembers: mocks.listGroupMembers,
      groupId: ref(1)
    })
  }
})

// Mock child components
const GroceryListItemStub = {
  template: '<div class="grocery-list-item-stub"></div>',
  props: ['name', 'quantityValue', 'quantityUnit', 'addedBy', 'note', 'modelValue']
}

describe('Lists Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Default mocks
    mocks.listLists.mockResolvedValue([{ id: 1, name: 'Groceries', type: 'grocery' }])
    mocks.listItems.mockResolvedValue([])
    mocks.listGroupMembers.mockResolvedValue([])
    mocks.addItem.mockResolvedValue({ id: 99, name: 'New Item', is_checked: false })
  })

  it('renders correctly', async () => {
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          GroceryListItem: GroceryListItemStub,
          NuxtLink: true
        }
      }
    })

    await flushPromises()
    expect(wrapper.exists()).toBe(true)
    expect(mocks.listLists).toHaveBeenCalled()
  })

  it('add button has accessible label', async () => {
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          GroceryListItem: GroceryListItemStub,
          NuxtLink: true
        }
      }
    })
    await flushPromises()

    const button = wrapper.find('button.bg-primary')
    expect(button.exists()).toBe(true)

    // This assertion expects the fix
    expect(button.attributes('aria-label')).toBe('Add item')
  })

  it('input field has accessible label', async () => {
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          GroceryListItem: GroceryListItemStub,
          NuxtLink: true
        }
      }
    })
    await flushPromises()

    const input = wrapper.find('input[type="text"]')
    expect(input.exists()).toBe(true)

    // This assertion expects the fix
    expect(input.attributes('aria-label')).toBe('New item name')
  })

  it('shows loading state when adding item', async () => {
    // Simulate slow network
    mocks.addItem.mockImplementation(async () => {
      await new Promise(resolve => setTimeout(resolve, 100))
      return { id: 99, name: 'New Item', is_checked: false }
    })

    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          GroceryListItem: GroceryListItemStub,
          NuxtLink: true
        }
      }
    })
    await flushPromises()

    const input = wrapper.find('input[type="text"]')
    const button = wrapper.find('button.bg-primary')

    await input.setValue('New Item')
    await button.trigger('click')

    // Expect loading state immediately after click
    expect(button.element.disabled).toBe(true)
    expect(input.element.disabled).toBe(true)

    // Check for spinner (assuming class name 'animate-spin')
    expect(wrapper.find('.animate-spin').exists()).toBe(true)

    // Wait for addItem to complete (simulated delay + promise resolution)
    // We need to wait more than 100ms.
    await new Promise(resolve => setTimeout(resolve, 150))
    await flushPromises()

    // Expect loading state cleared
    expect(button.element.disabled).toBe(false)
    expect(input.element.disabled).toBe(false)
    expect(wrapper.find('.animate-spin').exists()).toBe(false)
  })
})
