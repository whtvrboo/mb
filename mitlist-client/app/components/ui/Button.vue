<script setup lang="ts">
interface Props {
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  block?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  disabled: false,
  loading: false,
  variant: 'primary',
  block: false,
})

const classes = computed(() => {
  const base = [
    'inline-flex items-center justify-center px-4 py-2 rounded-lg font-bold text-lg',
    'border-[3px] border-background-dark',
    'shadow-neobrutalism active:translate-x-1 active:translate-y-1 active:shadow-none',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-x-0 disabled:translate-y-0',
    'transition-all duration-200',
  ]

  const variants = {
    primary: [
      'bg-primary text-background-dark',
      'hover:bg-[#dPb325]', // Slight darken for hover if needed, or just rely on partial transparency
    ],
    secondary: [
      'bg-white text-background-dark',
      'hover:bg-gray-50',
    ],
    outline: [
      'bg-transparent text-background-dark',
      'hover:bg-gray-50',
    ],
    ghost: [
      'border-transparent shadow-none',
      'text-background-dark',
      'hover:bg-gray-100',
      'active:translate-x-0 active:translate-y-0',
    ],
  }

  return [
    ...base,
    ...variants[props.variant || 'primary'],
    props.block ? 'w-full' : '',
  ]
})
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="classes"
  >
    <span v-if="loading" class="mr-2">
      <svg
        class="animate-spin h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </span>
    <slot />
  </button>
</template>
