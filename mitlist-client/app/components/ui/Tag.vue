<script setup lang="ts">
interface Props {
  variant?: 'default' | 'primary' | 'urgent' | 'kitchen'
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const classes = computed(() => {
  const base = [
    'inline-flex items-center px-4 py-2 border-[2px] border-background-dark rounded-full font-bold shadow-neobrutalism-sm',
    'text-sm'
  ]

  const variants = {
    default: 'bg-white text-background-dark',
    primary: 'bg-primary/30 text-background-dark',
    urgent: 'bg-[#8E9DB3] text-white',
    kitchen: 'bg-white text-background-dark', // Specific requested style
  }

  return [
    ...base,
    variants[props.variant] || variants.default
  ]
})
</script>

<template>
  <div :class="classes">
    <span v-if="icon" class="material-symbols-outlined text-[16px] mr-1">{{ icon }}</span>
    <slot />
  </div>
</template>
