<script setup lang="ts">
import { Label } from 'radix-vue'

interface Props {
  for?: string
  required?: boolean
}

withDefaults(defineProps<Props>(), {
  required: false,
})
</script>

<template>
  <Label
    :for="for"
    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
  >
    <slot />
    <span v-if="required" class="text-red-500 ml-1">*</span>
  </Label>
</template>
