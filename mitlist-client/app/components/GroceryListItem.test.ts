import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GroceryListItem from './GroceryListItem.vue'

describe('GroceryListItem', () => {
  it('renders label wrapping the name', () => {
    const wrapper = mount(GroceryListItem, {
      props: {
        name: 'Apples',
        modelValue: false
      }
    })

    const label = wrapper.find('label')
    expect(label.exists()).toBe(true)
    expect(label.text()).toContain('Apples')
  })

  it('renders checkbox input inside the label', () => {
    const wrapper = mount(GroceryListItem, {
      props: {
        name: 'Apples',
        modelValue: false
      }
    })

    const label = wrapper.find('label')
    const input = label.find('input[type="checkbox"]')

    expect(input.exists()).toBe(true)
  })

  it('preserves delete button outside the label', () => {
    const wrapper = mount(GroceryListItem, {
      props: {
        name: 'Apples',
        modelValue: false
      }
    })

    const label = wrapper.find('label')
    const button = wrapper.find('button')

    // Button should exist
    expect(button.exists()).toBe(true)

    // Button should NOT be inside the label
    expect(label.element.contains(button.element)).toBe(false)
  })
})
