import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListsPage from './lists.vue'

// Mock dependencies
vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: vi.fn().mockResolvedValue([]),
    createList: vi.fn(),
    listItems: vi.fn().mockResolvedValue([]),
    addItem: vi.fn(),
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

// Mock components used in the template
vi.mock('~/components/GroceryListItem.vue', () => ({
  default: { template: '<div>GroceryListItem</div>' }
}))

describe('Lists Page Accessibility', () => {
  it('renders with accessibility attributes', async () => {
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          NuxtLink: { template: '<a href="#"><slot /></a>' }
        }
      }
    })

    // Check back button aria-label
    const backButton = wrapper.find('a[href="#"]')
    expect(backButton.attributes('aria-label')).toBe('Go back to dashboard')

    // Check add item button aria-label
    const addButton = wrapper.find('button[aria-label="Add item"]')
    expect(addButton.exists()).toBe(true)

    // Check input label association
    const input = wrapper.find('input[placeholder="Add new item..."]')
    const inputId = input.attributes('id')
    expect(inputId).toBeTruthy()

    const label = wrapper.find(`label[for="${inputId}"]`)
    expect(label.exists()).toBe(true)
    expect(label.text()).toBe('Add new item')
    expect(label.classes()).toContain('sr-only')
  })
})
