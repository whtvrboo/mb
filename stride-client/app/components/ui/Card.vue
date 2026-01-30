<script setup lang="ts">
interface Props {
  variant?: 'default' | 'outlined'
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const cardClasses = computed(() => {
  const base = [
    'rounded-lg shadow-sm',
    'bg-white dark:bg-gray-800',
  ]

  if (props.variant === 'outlined') {
    base.push('border border-gray-200 dark:border-gray-700')
  } else {
    base.push('shadow-md')
  }

  return base
})
</script>

<template>
  <div :class="cardClasses">
    <div v-if="$slots.header" class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <slot name="header" />
    </div>
    <div class="px-6 py-4">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
      <slot name="footer" />
    </div>
  </div>
</template>
