<script setup lang="ts">
import { useId } from 'vue'

interface Props {
  modelValue?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  autocomplete?: string
  id?: string
  error?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  required: false,
  error: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputId = props.id || useId()

const classes = computed(() => [
  'w-full h-14 px-4 py-2 bg-white',
  'border-[3px] border-background-dark rounded-lg',
  'text-lg font-medium placeholder:text-gray-400',
  'shadow-neobrutalism transition-all',
  'focus:outline-none focus:ring-0 focus:border-primary',
  'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
  props.error
    ? 'border-red-500 focus:border-red-500'
    : '',
])
</script>

<template>
  <input
    :id="inputId"
    :aria-invalid="error"
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :required="required"
    :autocomplete="autocomplete"
    :class="classes"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
