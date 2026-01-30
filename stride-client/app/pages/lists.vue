<script setup lang="ts">
import { ref } from 'vue'
import GroceryListItem from '~/components/GroceryListItem.vue'

// Mock Data for now - will connect to useLists later
const items = ref([
  { id: 1, label: 'Avocados', quantity: 4, addedBy: 'You', category: 'Produce', checked: false },
  { id: 2, label: 'Bananas', quantity: 1, addedBy: 'Sarah', category: 'Produce', checked: false },
  { id: 3, label: 'Oat Milk', quantity: 2, addedBy: 'J', category: 'Pantry', note: 'Get the Barista blend specifically!', checked: false },
  { id: 4, label: 'Sourdough Bread', quantity: 1, addedBy: 'J', category: 'Pantry', checked: false },
  { id: 5, label: 'Eggs', quantity: 12, addedBy: 'You', category: 'Pantry', checked: true },
])

const newItem = ref('')

const addItem = () => {
    if (!newItem.value) return
    items.value.push({
        id: Date.now(),
        label: newItem.value,
        quantity: 1,
        addedBy: 'You',
        category: 'Uncategorized',
        checked: false
    })
    newItem.value = ''
}

const deleteItem = (id: number) => {
    items.value = items.value.filter(i => i.id !== id)
}

// Group items by category (Produce, Pantry, etc.)
const groupedItems = computed(() => {
    const groups: Record<string, typeof items.value> = {}
    items.value.forEach(item => {
        if (item.checked) return // Skip checked items here
        if (!groups[item.category]) groups[item.category] = []
        groups[item.category].push(item)
    })
    return groups
})

const checkedItems = computed(() => items.value.filter(i => i.checked))
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark min-h-screen flex flex-col items-center font-display text-background-dark dark:text-white">
    <!-- Mobile Container -->
    <div class="relative flex flex-col h-full w-full max-w-md bg-background-light dark:bg-background-dark border-x-[3px] border-background-dark overflow-hidden min-h-screen">
      
      <!-- Header -->
      <header class="shrink-0 bg-background-light dark:bg-background-dark pt-6 pb-2 px-5 z-10 border-b-[3px] border-background-dark">
        <div class="flex items-center justify-between mb-4">
          <NuxtLink to="/" class="flex items-center justify-center size-10 rounded-full border-[2px] border-background-dark hover:bg-background-dark hover:text-white transition-colors active:translate-y-[2px] active:translate-x-[2px] active:shadow-none shadow-neobrutalism-sm bg-white text-background-dark">
            <span class="material-symbols-outlined font-bold">arrow_back</span>
          </NuxtLink>
          
          <!-- Avatar Stack -->
          <div class="flex -space-x-3">
             <div class="size-10 rounded-full border-[2px] border-background-dark bg-primary shadow-neobrutalism-sm z-30 flex items-center justify-center font-bold">You</div>
             <div class="size-10 rounded-full border-[2px] border-background-dark bg-gray-200 shadow-neobrutalism-sm z-20 flex items-center justify-center font-bold">SM</div>
             <div class="size-10 rounded-full border-[2px] border-background-dark bg-white shadow-neobrutalism-sm z-10 flex items-center justify-center font-bold text-xs">+2</div>
          </div>
        </div>
        <h1 class="text-4xl font-bold tracking-tighter uppercase">Groceries</h1>
      </header>

      <!-- Scrollable List Area -->
      <main class="flex-1 overflow-y-auto p-5 pb-32">
        
        <!-- Categories -->
        <div v-for="(categoryItems, category) in groupedItems" :key="category" class="mb-6">
            <h3 
                class="text-lg font-bold border-b-[3px] border-background-dark inline-block pr-8 mb-4 px-2 py-1 shadow-neobrutalism-sm transform rounded-sm"
                :class="category === 'Produce' ? 'bg-primary -rotate-1' : 'bg-white rotate-1'"
            >
                {{ category }}
            </h3>

            <GroceryListItem 
                v-for="item in categoryItems" 
                :key="item.id"
                :label="item.label"
                :quantity="item.quantity"
                :added-by="item.addedBy"
                :note="item.note"
                v-model="item.checked"
                @delete="deleteItem(item.id)"
            />
        </div>

        <!-- Checked Items -->
        <div v-if="checkedItems.length > 0" class="mb-6">
            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">Completed</h3>
            <GroceryListItem 
                v-for="item in checkedItems" 
                :key="item.id"
                :label="item.label"
                :quantity="item.quantity"
                v-model="item.checked"
                @delete="deleteItem(item.id)"
            />
        </div>

        <div class="h-10"></div>
      </main>

      <!-- Sticky Bottom Input -->
      <div class="fixed md:absolute bottom-0 left-0 w-full bg-background-light p-4 z-20 border-t-[3px] border-background-dark max-w-md mx-auto">
        <div class="flex gap-3">
          <div class="relative flex-1">
            <input 
                v-model="newItem"
                @keyup.enter="addItem"
                class="w-full h-14 bg-white border-[3px] border-background-dark rounded-lg px-4 text-lg font-medium placeholder:text-gray-400 shadow-neobrutalism-sm focus:outline-none focus:ring-0 focus:shadow-neobrutalism focus:-translate-y-1 transition-all" 
                placeholder="Add new item..." 
                type="text"
            />
          </div>
          <button 
            @click="addItem"
            class="size-14 bg-primary border-[3px] border-background-dark rounded-lg shadow-neobrutalism-sm flex items-center justify-center hover:bg-[#ffe14f] active:shadow-none active:translate-y-[2px] active:translate-x-[2px] transition-all"
          >
            <span class="material-symbols-outlined text-background-dark text-3xl font-bold">add</span>
          </button>
        </div>
        <!-- Bottom safe area spacer -->
        <div class="h-4 w-full"></div>
      </div>

    </div>
  </div>
</template>
