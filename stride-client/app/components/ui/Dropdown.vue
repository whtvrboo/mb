<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface DropdownItem {
    label: string
    action?: () => void
    to?: string
    icon?: string
    danger?: boolean
}

interface Props {
    label?: string // Text for the trigger button
    items: DropdownItem[]
    icon?: string // Icon for the trigger button
}

const props = defineProps<Props>()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggle = () => {
    isOpen.value = !isOpen.value
}

const close = () => {
    isOpen.value = false
}

const handleClickOutside = (event: MouseEvent) => {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
        close()
    }
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})

const handleItemClick = (item: DropdownItem) => {
    if (item.action) {
        item.action()
    }
    close()
}
</script>

<template>
    <div class="relative inline-block text-left" ref="dropdownRef">
        <div @click="toggle">
            <slot name="trigger">
                <button type="button"
                    class="inline-flex items-center justify-center gap-2 rounded-lg border-[3px] border-background-dark bg-white px-4 py-2 font-bold shadow-[4px_4px_0px_0px_#221f10] transition-all hover:bg-gray-50 active:translate-x-1 active:translate-y-1 active:shadow-none"
                    :class="{ 'bg-gray-100 translate-x-1 translate-y-1 shadow-none': isOpen }">
                    <span v-if="icon" class="material-symbols-outlined">{{ icon }}</span>
                    <span v-if="label">{{ label }}</span>
                    <span class="material-symbols-outlined text-lg transition-transform"
                        :class="{ 'rotate-180': isOpen }">expand_more</span>
                </button>
            </slot>
        </div>

        <Transition enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95">
            <div v-if="isOpen"
                class="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-xl border-[3px] border-background-dark bg-white shadow-[6px_6px_0px_0px_#221f10] ring-1 ring-black ring-opacity-5 focus:outline-none overflow-hidden">
                <div class="py-2" role="none">
                    <template v-for="(item, index) in items" :key="index">
                        <!-- Custom Link/Action -->
                        <component :is="item.to ? 'NuxtLink' : 'button'" :to="item.to"
                            class="group flex w-full items-center px-4 py-3 text-sm font-bold transition-colors hover:bg-gray-50"
                            :class="item.danger ? 'text-red-600 hover:bg-red-50' : 'text-background-dark'"
                            @click="!item.to && handleItemClick(item)">
                            <span v-if="item.icon" class="material-symbols-outlined mr-3 text-[20px]"
                                :class="item.danger ? 'text-red-600' : 'text-gray-400 group-hover:text-background-dark'">{{
                                item.icon }}</span>
                            {{ item.label }}
                        </component>
                    </template>
                </div>
            </div>
        </Transition>
    </div>
</template>
