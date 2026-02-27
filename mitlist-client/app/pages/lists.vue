<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import GroceryListItem from '~/components/GroceryListItem.vue'
import { useLists } from '~/composables/useLists'
import { useAuth } from '~/composables/useAuth'
import type { ListResponse, ItemResponse } from '~/types/lists'
import type { GroupMemberResponse } from '~/types/auth'

const { listLists, createList, listItems, addItem, deleteItem: apiDeleteItem, updateItem } = useLists()
const { listGroupMembers, groupId } = useAuth()

// State
const lists = ref<ListResponse[]>([])
const currentListId = ref<number | null>(null)
const items = ref<ItemResponse[]>([])
const members = ref<GroupMemberResponse[]>([])
const newItemName = ref('')
const isLoading = ref(true)
const isAdding = ref(false)

// Fetch Data
const fetchData = async () => {
  isLoading.value = true
  try {
    // 1. Fetch group members for user resolution
    if (groupId.value) {
      members.value = await listGroupMembers(groupId.value)
    }

    // 2. Fetch Lists
    lists.value = await listLists()

    // 3. Select first list or create default if none
    if (lists.value.length === 0 && groupId.value) {
      const newList = await createList({
        group_id: groupId.value,
        name: 'Groceries',
        type: 'grocery'
      })
      lists.value = [newList]
      currentListId.value = newList.id
    } else if (lists.value.length > 0) {
      // Prefer a list named 'Groceries' or just the first one
      const defaultList = lists.value.find(l => l.name === 'Groceries') || lists.value[0]
      currentListId.value = defaultList.id
    }

    // 4. Fetch Items for current list
    if (currentListId.value) {
      items.value = await listItems(currentListId.value)
    }
  } catch (error) {
    console.error('Failed to fetch list data', error)
  } finally {
    isLoading.value = false
  }
}

// Actions
const handleAddItem = async () => {
  if (!newItemName.value || !currentListId.value || !groupId.value) return

  isAdding.value = true
  try {
    const newItem = await addItem(currentListId.value, {
      list_id: currentListId.value,
      name: newItemName.value,
      quantity_value: 1,
      is_checked: false
    })
    items.value.push(newItem)
    newItemName.value = ''
  } catch (e) {
    console.error('Failed to add item', e)
  } finally {
    isAdding.value = false
  }
}

const handleDeleteItem = async (itemId: number) => {
  if (!currentListId.value) return
  try {
    await apiDeleteItem(currentListId.value, itemId)
    items.value = items.value.filter(i => i.id !== itemId)
  } catch (e) {
    console.error('Failed to delete item', e)
  }
}

const handleToggleItem = async (item: ItemResponse) => {
  if (!currentListId.value) return
  try {
    const updated = await updateItem(currentListId.value, item.id, {
      is_checked: item.is_checked
    })
    // Update local state with response (e.g. checked_at timestamp)
    Object.assign(item, updated)
  } catch (e) {
    console.error('Failed to update item', e)
    // Revert on failure
    item.is_checked = !item.is_checked
  }
}

// Helpers
const getMemberName = (userId: number | null) => {
  if (!userId) return ''
  const member = members.value.find(m => m.user_id === userId)
  return member ? (member.user?.name || member.user?.email || 'User') : 'Unknown'
}

// Computed Grouping
// Since API doesn't have categories, we group by "Pending" vs "Completed" for now, or just "Items"
// If we want categories, we'd need to add that field to API or infer it. For now, fallback to flat list or checked separation.
const activeItems = computed(() => items.value.filter(i => !i.is_checked))
const checkedItems = computed(() => items.value.filter(i => i.is_checked))

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div
    class="bg-background-light dark:bg-background-dark min-h-screen flex flex-col items-center font-display text-background-dark dark:text-white">
    <!-- Mobile Container -->
    <div
      class="relative flex flex-col h-full w-full max-w-md bg-background-light dark:bg-background-dark border-x-[3px] border-background-dark overflow-hidden min-h-screen">

      <!-- Header -->
      <header
        class="shrink-0 bg-background-light dark:bg-background-dark pt-6 pb-2 px-5 z-10 border-b-[3px] border-background-dark">
        <div class="flex items-center justify-between mb-4">
          <NuxtLink to="/"
            aria-label="Go back"
            class="flex items-center justify-center size-10 rounded-full border-[2px] border-background-dark hover:bg-background-dark hover:text-white transition-colors active:translate-y-[2px] active:translate-x-[2px] active:shadow-none shadow-neobrutalism-sm bg-white text-background-dark">
            <span class="material-symbols-outlined font-bold">arrow_back</span>
          </NuxtLink>

          <!-- Avatar Stack -->
          <div class="flex -space-x-3">
            <div v-for="(member, idx) in members.slice(0, 3)" :key="member.user_id"
              class="size-10 rounded-full border-[2px] border-background-dark shadow-neobrutalism-sm z-30 flex items-center justify-center font-bold text-xs bg-white overflow-hidden"
              :style="{ zIndex: 30 - idx }">
              <span v-if="member.user?.avatar_url">
                <img :src="member.user.avatar_url" class="w-full h-full object-cover" />
              </span>
              <span v-else>{{ member.user?.name?.[0] || '?' }}</span>
            </div>
            <div v-if="members.length > 3"
              class="size-10 rounded-full border-[2px] border-background-dark bg-white shadow-neobrutalism-sm z-0 flex items-center justify-center font-bold text-xs">
              +{{ members.length - 3 }}
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between">
          <h1 class="text-4xl font-bold tracking-tighter uppercase">Groceries</h1>
          <div v-if="isLoading"
            class="size-6 border-2 border-background-dark border-t-transparent rounded-full animate-spin"></div>
        </div>
      </header>

      <!-- Scrollable List Area -->
      <main class="flex-1 overflow-y-auto p-5 pb-32">

        <div v-if="items.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-10 opacity-60">
          <span class="material-symbols-outlined text-6xl mb-2">shopping_basket</span>
          <p class="font-bold">List is empty</p>
        </div>

        <!-- Active Items -->
        <div v-if="activeItems.length > 0" class="mb-6">
          <h3
            class="text-lg font-bold border-b-[3px] border-background-dark inline-block pr-8 mb-4 px-2 py-1 shadow-neobrutalism-sm transform rounded-sm bg-white -rotate-1">
            To Buy
          </h3>

          <GroceryListItem v-for="item in activeItems" :key="item.id" :name="item.name"
            :quantity-value="item.quantity_value" :quantity-unit="item.quantity_unit"
            :added-by="getMemberName(item.added_by_id)" :note="item.notes" v-model="item.is_checked"
            @update:model-value="handleToggleItem(item)" @delete="handleDeleteItem(item.id)" />
        </div>

        <!-- Checked Items -->
        <div v-if="checkedItems.length > 0" class="mb-6">
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">Completed</h3>
          <GroceryListItem v-for="item in checkedItems" :key="item.id" :name="item.name"
            :quantity-value="item.quantity_value" :quantity-unit="item.quantity_unit"
            :added-by="getMemberName(item.added_by_id)" :note="item.notes" v-model="item.is_checked"
            @update:model-value="handleToggleItem(item)" @delete="handleDeleteItem(item.id)" />
        </div>

        <div class="h-10"></div>
      </main>

      <!-- Sticky Bottom Input -->
      <div
        class="fixed md:absolute bottom-0 left-0 w-full bg-background-light p-4 z-20 border-t-[3px] border-background-dark max-w-md mx-auto">
        <div class="flex gap-3">
          <div class="relative flex-1">
            <input v-model="newItemName" @keyup.enter="handleAddItem" :disabled="isLoading || !currentListId || isAdding"
              aria-label="New item name"
              class="w-full h-14 bg-white border-[3px] border-background-dark rounded-lg px-4 text-lg font-medium placeholder:text-gray-400 shadow-neobrutalism-sm focus:outline-none focus:ring-0 focus:shadow-neobrutalism focus:-translate-y-1 transition-all disabled:opacity-50"
              placeholder="Add new item..." type="text" />
          </div>
          <button @click="handleAddItem" :disabled="isLoading || !currentListId || isAdding"
            aria-label="Add item"
            class="size-14 bg-primary border-[3px] border-background-dark rounded-lg shadow-neobrutalism-sm flex items-center justify-center hover:bg-[#ffe14f] active:shadow-none active:translate-y-[2px] active:translate-x-[2px] transition-all disabled:opacity-50">
            <span v-if="!isAdding" class="material-symbols-outlined text-background-dark text-3xl font-bold">add</span>
            <div v-else class="size-6 border-4 border-background-dark border-t-transparent rounded-full animate-spin"></div>
          </button>
        </div>
        <!-- Bottom safe area spacer -->
        <div class="h-4 w-full"></div>
      </div>

    </div>
  </div>
</template>
