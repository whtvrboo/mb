import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListsPage from '../app/pages/lists.vue'
import { ref } from 'vue'

// Define mock functions using vi.hoisted to allow access inside vi.mock
const mocks = vi.hoisted(() => {
  return {
    listLists: vi.fn(),
    createList: vi.fn(),
    listItems: vi.fn(),
    addItem: vi.fn(),
    deleteItem: vi.fn(),
    updateItem: vi.fn(),
    listGroupMembers: vi.fn(),
    groupId: { value: 1 } // Simulating a Ref
  }
})

// Mock Composables
vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: mocks.listLists,
    createList: mocks.createList,
    listItems: mocks.listItems,
    addItem: mocks.addItem,
    deleteItem: mocks.deleteItem,
    updateItem: mocks.updateItem
  })
}))

vi.mock('~/composables/useAuth', () => ({
  useAuth: () => ({
    listGroupMembers: mocks.listGroupMembers,
    groupId: mocks.groupId
  })
}))

// Mock components
const GroceryListItemStub = {
  template: '<div><slot /></div>',
  props: ['name', 'quantityValue', 'quantityUnit', 'addedBy', 'note', 'modelValue']
}

const NuxtLinkStub = {
  template: '<a><slot /></a>'
}

describe('Lists Page', () => {
  it('renders accessible elements', async () => {
    // Setup default mock returns
    mocks.listLists.mockResolvedValue({ data: { value: [] } })
    mocks.listItems.mockResolvedValue({ data: { value: [] } })
    mocks.listGroupMembers.mockResolvedValue({ data: { value: [] } })
    mocks.createList.mockResolvedValue({ id: 1, name: 'New List' })

    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          NuxtLink: NuxtLinkStub,
          GroceryListItem: GroceryListItemStub
        }
      }
    })

    // Wait for initial fetch
    await new Promise(resolve => setTimeout(resolve, 0))

    // Check Back Button
    const backBtn = wrapper.find('a[aria-label="Go back to dashboard"]')
    expect(backBtn.exists()).toBe(true)

    // Check Input
    const input = wrapper.find('input[aria-label="New item name"]')
    expect(input.exists()).toBe(true)

    // Check Add Button
    const addBtn = wrapper.find('button[aria-label="Add item"]')
    expect(addBtn.exists()).toBe(true)
  })

  it('shows loading spinner when adding item', async () => {
    // Setup default mock returns
    mocks.listLists.mockResolvedValue({ data: { value: [{ id: 1, name: 'Groceries' }] } })
    mocks.listItems.mockResolvedValue({ data: { value: [] } })
    mocks.listGroupMembers.mockResolvedValue({ data: { value: [] } })

    // Control addItem resolution
    let resolveAddItem: (val: any) => void
    const addItemPromise = new Promise((resolve) => {
      resolveAddItem = resolve
    })
    mocks.addItem.mockReturnValue(addItemPromise)

    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          NuxtLink: NuxtLinkStub,
          GroceryListItem: GroceryListItemStub
        }
      }
    })

    // Wait for initial fetch
    await new Promise(resolve => setTimeout(resolve, 0))

    // Set input value
    const input = wrapper.find('input[aria-label="New item name"]')
    await input.setValue('Milk')

    // Find add button
    const addBtn = wrapper.find('button[aria-label="Add item"]')

    // Click add
    await addBtn.trigger('click')

    // Check if spinner is visible (class animate-spin)
    const spinner = wrapper.find('.animate-spin')
    expect(spinner.exists()).toBe(true)

    // Button should be disabled
    expect(addBtn.element.disabled).toBe(true)

    // Resolve promise
    resolveAddItem!({ id: 1, name: 'Milk' })

    // Wait for promise resolution (requires microtask flush)
    await new Promise(resolve => setTimeout(resolve, 0))

    // Spinner should be gone
    expect(wrapper.find('.animate-spin').exists()).toBe(false)

    // Button enabled again
    expect(addBtn.element.disabled).toBe(false)
  })
})
