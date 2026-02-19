import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListsPage from './lists.vue'
import { ref } from 'vue'

// Mock composables
const mockAddItem = vi.fn()
const mockListLists = vi.fn()
const mockListItems = vi.fn()

vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: mockListLists,
    listItems: mockListItems,
    addItem: mockAddItem,
    createList: vi.fn(),
    deleteItem: vi.fn(),
    updateItem: vi.fn()
  })
}))

vi.mock('~/composables/useAuth', () => ({
  useAuth: () => ({
    listGroupMembers: vi.fn().mockResolvedValue([]),
    groupId: ref(1)
  })
}))

// Mock Nuxt components
const NuxtLink = {
  template: '<a href="#"><slot /></a>'
}

describe('ListsPage', () => {
  it('renders correctly and handles add item interaction', async () => {
    // Setup mocks
    mockListLists.mockResolvedValue({ data: ref([{ id: 1, name: 'Groceries' }]) })
    mockListItems.mockResolvedValue({ data: ref([]) })

    // Mount
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          NuxtLink,
          GroceryListItem: true
        }
      }
    })

    // Wait for fetch
    await new Promise(resolve => setTimeout(resolve, 0))
    await wrapper.vm.$nextTick()

    // Check loading is false (initially true, then false after fetch)
    // We might need to wait for promises.
    // However, we can check static attributes first.

    // 1. Check ARIA labels
    const input = wrapper.find('input[placeholder="Add new item..."]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('aria-label')).toBe('New item name')

    const addButton = wrapper.find('button[aria-label="Add item"]')
    expect(addButton.exists()).toBe(true)

    const backButton = wrapper.find('a[aria-label="Go back to dashboard"]')
    expect(backButton.exists()).toBe(true)

    // 2. Check interaction (Spinner)
    // Make addItem hang to test loading state
    let finishAdd: () => void
    const addPromise = new Promise<void>(resolve => {
      finishAdd = resolve
    })
    mockAddItem.mockImplementation(async () => {
      await addPromise
      return { id: 2, name: 'New Item' }
    })

    await input.setValue('Milk')
    await addButton.trigger('click')

    // Now isAdding should be true
    // We check if spinner exists
    // The spinner div has class 'animate-spin'
    const spinner = wrapper.find('.animate-spin')
    expect(spinner.exists()).toBe(true)

    // Button should be disabled
    expect(addButton.attributes('disabled')).toBeDefined()
    expect(input.attributes('disabled')).toBeDefined()

    // Finish add
    if (finishAdd!) finishAdd()

    // Wait for async
    await new Promise(resolve => setTimeout(resolve, 0))
    await wrapper.vm.$nextTick()

    // Spinner should be gone
    expect(wrapper.find('.animate-spin').exists()).toBe(false)
  })
})
