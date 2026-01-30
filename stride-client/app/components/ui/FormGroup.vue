<script setup lang="ts">
import Label from './Label.vue'

interface Props {
  label?: string
  name?: string
  error?: string
  required?: boolean
}

withDefaults(defineProps<Props>(), {
  required: false,
})
</script>

<template>
  <div class="space-y-1">
    <Label v-if="label" :for="name" :required="required">
      {{ label }}
    </Label>
    <slot />
    <p v-if="error" class="text-sm text-red-600 dark:text-red-400 mt-1">
      {{ error }}
    </p>
  </div>
</template>
