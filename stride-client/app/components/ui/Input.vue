<script setup lang="ts">
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

const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`

const classes = computed(() => [
  'w-full px-3 py-2 border rounded-md shadow-sm',
  'focus:outline-none focus:ring-2 focus:ring-offset-2',
  'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
  'dark:bg-gray-800 dark:text-gray-100 dark:border-gray-700',
  props.error
    ? 'border-red-500 focus:ring-red-500 dark:border-red-500'
    : 'border-gray-300 focus:ring-primary-500 dark:border-gray-600',
])
</script>

<template>
  <input
    :id="inputId"
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
