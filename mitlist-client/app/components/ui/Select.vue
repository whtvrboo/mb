<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

interface Option {
    label: string
    value: string | number
}

interface Props {
    modelValue: string | number | null
    options: Option[]
    placeholder?: string
    label?: string
    disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    modelValue: null,
    options: () => [],
    placeholder: 'Select an option',
    disabled: false
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const selectRef = ref<HTMLElement | null>(null)

const selectedOption = computed(() => {
    return props.options.find(opt => opt.value === props.modelValue)
})

const toggle = () => {
    if (!props.disabled) {
        isOpen.value = !isOpen.value
    }
}

const close = () => {
    isOpen.value = false
}

const selectOption = (option: Option) => {
    emit('update:modelValue', option.value)
    close()
}

const handleClickOutside = (event: MouseEvent) => {
    if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
        close()
    }
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
    <div class="flex flex-col gap-2" ref="selectRef">
        <label v-if="label" class="font-bold text-sm uppercase ml-1 block">{{ label }}</label>
        <div class="relative">
            <button type="button"
                class="relative w-full cursor-default bg-white border-[3px] border-background-dark rounded-lg py-3.5 pl-4 pr-10 text-left shadow-[4px_4px_0px_0px_#221f10] focus:outline-none focus:ring-0 focus:border-primary transition-all active:translate-x-0.5 active:translate-y-0.5 active:shadow-[2px_2px_0px_0px_#221f10]"
                :class="[
                    disabled ? 'opacity-50 cursor-not-allowed bg-gray-100' : 'cursor-pointer hover:bg-gray-50',
                    isOpen ? 'ring-2 ring-primary border-primary' : ''
                ]" @click="toggle">
                <span class="block truncate font-bold text-lg"
                    :class="selectedOption ? 'text-background-dark' : 'text-gray-400 font-medium'">
                    {{ selectedOption ? selectedOption.label : placeholder }}
                </span>
                <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <span class="material-symbols-outlined text-gray-500 transition-transform duration-200"
                        :class="{ 'rotate-180': isOpen }">
                        expand_more
                    </span>
                </span>
            </button>

            <Transition enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95">
                <div v-if="isOpen"
                    class="absolute z-60 mt-2 max-h-60 w-full overflow-auto rounded-lg border-[3px] border-background-dark bg-white py-1 shadow-[6px_6px_0px_0px_#221f10] focus:outline-none sm:text-sm">
                    <ul role="listbox">
                        <li v-for="option in options" :key="option.value"
                            class="relative cursor-pointer select-none py-3 pl-4 pr-9 hover:bg-primary/20 transition-colors"
                            :class="{ 'bg-primary/10': option.value === modelValue }" role="option"
                            @click="selectOption(option)">
                            <span class="block truncate font-bold text-base"
                                :class="{ 'text-primary-900': option.value === modelValue, 'text-background-dark': option.value !== modelValue }">
                                {{ option.label }}
                            </span>
                            <span v-if="option.value === modelValue"
                                class="absolute inset-y-0 right-0 flex items-center pr-4 text-primary-600">
                                <span class="material-symbols-outlined font-bold text-[20px]">check</span>
                            </span>
                        </li>
                    </ul>
                </div>
            </Transition>
        </div>
    </div>
</template>
