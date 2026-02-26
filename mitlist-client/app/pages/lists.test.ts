import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListsPage from './lists.vue'

// Mock useLists composable
vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: vi.fn().mockResolvedValue([]),
    createList: vi.fn().mockResolvedValue({ id: 1, name: 'Groceries' }), // Return a valid list on create
    listItems: vi.fn().mockResolvedValue([]),
    addItem: vi.fn(),
    deleteItem: vi.fn(),
    updateItem: vi.fn(),
  }),
}))

// Mock useAuth composable
vi.mock('~/composables/useAuth', () => ({
  useAuth: () => ({
    listGroupMembers: vi.fn().mockResolvedValue([]),
    groupId: { value: 1 },
  }),
}))

// Mock Nuxt components
vi.mock('~/components/GroceryListItem.vue', () => ({
  default: { template: '<div>GroceryListItem</div>' }
}))

// Mock Nuxt runtime config
vi.mock('nuxt/app', () => ({
  useRuntimeConfig: () => ({ public: {} }),
  useNuxtApp: () => ({})
}))

const stubs = {
  NuxtLink: { template: '<a><slot /></a>' }
}

describe('Lists Page', () => {
  it('renders input with correct aria-label', async () => {
    const wrapper = mount(ListsPage, {
      global: { stubs }
    })

    // Check input aria-label
    const input = wrapper.find('input[aria-label="New item name"]')
    expect(input.exists()).toBe(true)
  })

  it('renders add button with correct aria-label', async () => {
    const wrapper = mount(ListsPage, {
      global: { stubs }
    })

    // Check button aria-label
    const button = wrapper.find('button[aria-label="Add item"]')
    expect(button.exists()).toBe(true)
  })
})
