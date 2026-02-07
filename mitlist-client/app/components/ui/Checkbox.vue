<script setup lang="ts">
import { computed, useId } from 'vue'

interface Props {
    modelValue?: boolean | any[]
    value?: any
    label?: string
    disabled?: boolean
    id?: string
}

const props = withDefaults(defineProps<Props>(), {
    modelValue: false,
    disabled: false
})

const emit = defineEmits(['update:modelValue'])

const isChecked = computed(() => {
    if (Array.isArray(props.modelValue)) {
        return props.modelValue.includes(props.value)
    }
    return props.modelValue
})

const handleChange = (e: Event) => {
    const target = e.target as HTMLInputElement
    const checked = target.checked

    if (Array.isArray(props.modelValue)) {
        const newValue = [...props.modelValue]
        if (checked) {
            newValue.push(props.value)
        } else {
            const index = newValue.indexOf(props.value)
            if (index > -1) newValue.splice(index, 1)
        }
        emit('update:modelValue', newValue)
    } else {
        emit('update:modelValue', checked)
    }
}

const generatedId = useId()
const inputId = computed(() => props.id || generatedId)
</script>

<template>
    <div class="flex items-center gap-3">
        <div class="relative flex items-center">
            <input type="checkbox" :id="inputId" :checked="isChecked" :value="value" :disabled="disabled"
                @change="handleChange"
                class="peer appearance-none size-6 border-[3px] border-background-dark rounded bg-white checked:bg-primary transition-colors cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-background-dark" />

            <!-- Checkmark -->
            <span
                class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity">
                <span class="material-symbols-outlined text-[20px] font-bold text-background-dark">check</span>
            </span>
        </div>

        <label v-if="label" :for="inputId" class="font-bold text-lg cursor-pointer select-none"
            :class="disabled ? 'text-gray-400 cursor-not-allowed' : 'text-background-dark'">
            {{ label }}
        </label>
    </div>
</template>
