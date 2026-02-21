import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ListsPage from './lists.vue'
import { ref } from 'vue'

// Mock composables
vi.mock('~/composables/useLists', () => ({
  useLists: () => ({
    listLists: vi.fn().mockResolvedValue([{ id: 1, name: 'Groceries' }]),
    listItems: vi.fn().mockResolvedValue([]),
    addItem: vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100))),
    deleteItem: vi.fn(),
    createList: vi.fn()
  })
}))

vi.mock('~/composables/useAuth', () => ({
  useAuth: () => ({
    listGroupMembers: vi.fn().mockResolvedValue([]),
    groupId: ref(1)
  })
}))

// Mock GroceryListItem since we are testing the page
const GroceryListItem = {
  template: '<div class="grocery-item"></div>',
  props: ['name', 'quantityValue', 'quantityUnit', 'addedBy', 'note', 'modelValue']
}

describe('Lists Page', () => {
  it('has accessible elements', async () => {
    const wrapper = mount(ListsPage, {
      global: {
        stubs: {
          NuxtLink: {
            template: '<a href="#" class="nuxt-link"><slot /></a>'
          },
          GroceryListItem
        }
      }
    })

    // Wait for initial fetch
    await new Promise(resolve => setTimeout(resolve, 10))
    await wrapper.vm.$nextTick()

    // Check Input ARIA label
    const input = wrapper.find('input[aria-label="New item name"]')
    expect(input.exists()).toBe(true)

    // Check Add Button ARIA label
    const addButton = wrapper.find('button[aria-label="Add item"]')
    expect(addButton.exists()).toBe(true)

    // Check Back Link ARIA label
    const backLink = wrapper.find('.nuxt-link[aria-label="Go back to dashboard"]')
    expect(backLink.exists()).toBe(true)
  })
})
