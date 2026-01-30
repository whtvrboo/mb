<script setup lang="ts">
import { ref } from 'vue'

// Modal State
const showModal = ref(false)

// Toast State
const showToast = ref(false)
const toastVariant = ref<'success' | 'error' | 'warning' | 'info'>('success')

// Dropdown Items
const dropdownItems = [
    { label: 'Profile', icon: 'person' },
    { label: 'Settings', icon: 'settings', to: '/settings' },
    { label: 'Logout', icon: 'logout', danger: true, action: () => console.log('Logout clicked') }
]

// Select State
const selectedFruit = ref('apple')
const fruits = [
    { label: 'Apple', value: 'apple' },
    { label: 'Banana', value: 'banana' },
    { label: 'Orange', value: 'orange' },
    { label: 'Mango', value: 'mango' }
]

// Checkbox State
const isChecked = ref(true)
const selectedRoles = ref(['editor'])

// Radio State
const selectedPlan = ref('free')

// Table Data
const tableColumns = [
    { key: 'name', label: 'Name' },
    { key: 'role', label: 'Role' },
    { key: 'status', label: 'Status' }
]
const tableRows = [
    { name: 'Alice', role: 'Admin', status: 'Active' },
    { name: 'Bob', role: 'Editor', status: 'Inactive' },
    { name: 'Charlie', role: 'Viewer', status: 'Active' }
]

// Pagination State
const currentPage = ref(1)
</script>

<template>
    <div class="p-10 space-y-12 max-w-4xl mx-auto pb-32">
        <h1 class="text-3xl font-bold border-b-[3px] border-background-dark pb-4">UI Component Playground</h1>

        <!-- Modal -->
        <section class="space-y-4">
            <h2 class="text-xl font-bold uppercase text-gray-500">Modal</h2>
            <Button @click="showModal = true">Open Modal</Button>
            <Modal v-model="showModal" title="Example Modal">
                <p class="text-lg">This is a neobrutalist modal dialog.</p>
                <template #footer>
                    <Button variant="ghost" @click="showModal = false">Cancel</Button>
                    <Button @click="showModal = false">Confirm</Button>
                </template>
            </Modal>
        </section>

        <!-- Toast -->
        <section class="space-y-4">
            <h2 class="text-xl font-bold uppercase text-gray-500">Toast</h2>
            <div class="flex gap-2">
                <Button @click="{ showToast = true; toastVariant = 'success' }"
                    class="bg-sage text-white border-sage">Success</Button>
                <Button @click="{ showToast = true; toastVariant = 'error' }"
                    class="bg-red-200 text-red-900 border-red-900">Error</Button>
                <Button @click="{ showToast = true; toastVariant = 'warning' }"
                    class="bg-orange-200 text-orange-900 border-orange-900">Warning</Button>
            </div>
            <Toast v-model="showToast" :variant="toastVariant" title="Notification"
                message="This is a toast message component." />
        </section>

        <!-- Dropdown -->
        <section class="space-y-4">
            <h2 class="text-xl font-bold uppercase text-gray-500">Dropdown</h2>
            <Dropdown label="Options" icon="menu" :items="dropdownItems" />
        </section>

        <!-- Select -->
        <section class="space-y-4">
            <h2 class="text-xl font-bold uppercase text-gray-500">Select</h2>
            <div class="max-w-xs">
                <Select v-model="selectedFruit" :options="fruits" label="Favorite Fruit" />
            </div>
            <p class="text-sm font-mono mt-2">Selected: {{ selectedFruit }}</p>
        </section>

        <!-- Checkbox & Radio -->
        <section class="space-y-4">
            <h2 class="text-xl font-bold uppercase text-gray-500">Toggles</h2>
            <div class="flex flex-col gap-4">
                <Checkbox v-model="isChecked" label="Agree to Terms" />

                <div class="flex gap-6">
                    <Checkbox v-model="selectedRoles" value="admin" label="Admin" />
                    <Checkbox v-model="selectedRoles" value="editor" label="Editor" />
                    <Checkbox v-model="selectedRoles" value="viewer" label="Viewer" />
                </div>
                <p class="text-sm font-mono">Roles: {{ selectedRoles }}</p>

                <div class="flex gap-6 mt-2">
                    <Radio v-model="selectedPlan" value="free" label="Free Plan" name="plan" />
                    <Radio v-model="selectedPlan" value="pro" label="Pro Plan" name="plan" />
                </div>
                <p class="text-sm font-mono">Plan: {{ selectedPlan }}</p>
            </div>
        </section>

        <!-- Table -->
        <section class="space-y-4">
            <h2 class="text-xl font-bold uppercase text-gray-500">Table</h2>
            <Table :columns="tableColumns" :rows="tableRows" />
        </section>

        <!-- Pagination -->
        <section class="space-y-4">
            <h2 class="text-xl font-bold uppercase text-gray-500">Pagination</h2>
            <Pagination v-model:currentPage="currentPage" :totalPages="10" />
            <p class="text-center text-sm font-mono mt-2">Page: {{ currentPage }}</p>
        </section>
    </div>
</template>
