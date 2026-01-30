<script setup lang="ts">
interface Props {
  variant?: 'error' | 'warning' | 'info' | 'success'
  title?: string
}

withDefaults(defineProps<Props>(), {
  variant: 'info',
})

const classes = computed(() => {
  const variants = {
    error: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-200',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-200',
    info: 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-200',
    success: 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-200',
  }

  return [
    'border rounded-md p-4',
    variants[variant],
  ]
})
</script>

<template>
  <div :class="classes">
    <div v-if="title" class="font-semibold mb-1">
      {{ title }}
    </div>
    <div>
      <slot />
    </div>
  </div>
</template>
