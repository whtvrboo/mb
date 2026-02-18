import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GroceryListItem from './GroceryListItem.vue'

describe('GroceryListItem', () => {
  it('renders with correct focus styles on delete button', () => {
    const wrapper = mount(GroceryListItem, {
      props: {
        name: 'Milk',
        modelValue: false
      }
    })
    const button = wrapper.find('button[aria-label="Delete Milk"]')
    expect(button.exists()).toBe(true)
    expect(button.classes()).toContain('focus-visible:opacity-100')
    expect(button.classes()).toContain('focus-visible:ring-2')
  })

  it('toggles checkbox when clicking on the item name', async () => {
    const wrapper = mount(GroceryListItem, {
      props: {
        name: 'Milk',
        modelValue: false
      },
      attachTo: document.body // Sometimes needed for event propagation
    })

    const text = wrapper.find('span.text-xl')
    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('Milk')

    await text.trigger('click')

    // This should fail initially because the text is not associated with the checkbox
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([true])

    wrapper.unmount()
  })
})
