<script setup lang="ts">
interface Props {
  variant?: 'error' | 'warning' | 'info' | 'success'
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
})

const iconName = computed(() => {
    switch (props.variant) {
        case 'success': return 'check_circle'
        case 'error': return 'error'
        case 'warning': return 'warning'
        default: return 'info'
    }
})

const role = computed(() => {
    return ['error', 'warning'].includes(props.variant) ? 'alert' : 'status'
})

const classes = computed(() => {
  const variants = {
    error: 'bg-red-50 text-red-900',
    warning: 'bg-amber-50 text-amber-900',
    info: 'bg-blue-50 text-blue-900',
    success: 'bg-green-50 text-green-900',
  }

  return [
    'relative flex items-start gap-3 p-4 rounded-lg border-[3px] border-background-dark shadow-neobrutalism',
    variants[props.variant],
  ]
})

const iconClasses = computed(() => {
    switch (props.variant) {
        case 'error': return 'text-red-700'
        case 'warning': return 'text-amber-700'
        case 'success': return 'text-green-700'
        default: return 'text-blue-700'
    }
})
</script>

<template>
  <div :class="classes" :role="role">
    <span class="material-symbols-outlined text-2xl shrink-0" :class="iconClasses" aria-hidden="true">
      {{ iconName }}
    </span>
    <div class="flex-1">
      <h5 v-if="title" class="font-bold text-lg leading-tight mb-1">
        {{ title }}
      </h5>
      <div class="text-sm font-medium leading-relaxed opacity-90">
        <slot />
      </div>
    </div>
  </div>
</template>
