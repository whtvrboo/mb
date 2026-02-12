<script setup lang="ts">
import { computed, useId } from 'vue'

interface Props {
    modelValue?: any
    value?: any
    label?: string
    name?: string
    disabled?: boolean
    id?: string
}

const props = withDefaults(defineProps<Props>(), {
    disabled: false
})

const emit = defineEmits(['update:modelValue'])

const isChecked = computed(() => {
    return props.modelValue === props.value
})

const handleChange = () => {
    if (!props.disabled) {
        emit('update:modelValue', props.value)
    }
}

const generatedId = useId()
const inputId = computed(() => props.id || generatedId)
</script>

<template>
    <div class="flex items-center gap-3">
        <div class="relative flex items-center justify-center">
            <input type="radio" :id="inputId" :name="name" :value="value" :disabled="disabled" :checked="isChecked"
                @change="handleChange"
                class="peer appearance-none size-6 border-[3px] border-background-dark rounded-full bg-white transition-colors cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-background-dark" />

            <!-- Inner dot -->
            <div
                aria-hidden="true"
                class="absolute size-3 bg-background-dark rounded-full pointer-events-none scale-0 peer-checked:scale-100 transition-transform duration-200">
            </div>
        </div>

        <label v-if="label" :for="inputId" class="font-bold text-lg cursor-pointer select-none"
            :class="disabled ? 'text-gray-400 cursor-not-allowed' : 'text-background-dark'">
            {{ label }}
        </label>
    </div>
</template>
