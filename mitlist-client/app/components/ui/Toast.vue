<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

interface Props {
    modelValue: boolean
    title?: string
    message?: string
    variant?: 'success' | 'error' | 'warning' | 'info'
    duration?: number
    position?: 'top-right' | 'bottom-right' | 'top-center' | 'bottom-center'
}

const props = withDefaults(defineProps<Props>(), {
    modelValue: false,
    variant: 'info',
    duration: 3000,
    position: 'bottom-right',
})

const emit = defineEmits(['update:modelValue'])

let timer: number | undefined

const startTimer = () => {
    if (props.duration > 0) {
        timer = window.setTimeout(() => {
            emit('update:modelValue', false)
        }, props.duration)
    }
}

const clearTimer = () => {
    if (timer) clearTimeout(timer)
}

const close = () => {
    clearTimer()
    emit('update:modelValue', false)
}

onMounted(() => {
    if (props.modelValue) startTimer()
})

watch(() => props.modelValue, (val) => {
    if (val) startTimer()
    else clearTimer()
})

onUnmounted(() => {
    clearTimer()
})

const positionClasses = computed(() => {
    switch (props.position) {
        case 'top-right': return 'top-4 right-4'
        case 'bottom-right': return 'bottom-4 right-4'
        case 'top-center': return 'top-4 left-1/2 -translate-x-1/2'
        case 'bottom-center': return 'bottom-4 left-1/2 -translate-x-1/2'
        default: return 'bottom-4 right-4'
    }
})

const variantClasses = computed(() => {
    switch (props.variant) {
        case 'success': return 'bg-background-dark text-white shadow-[4px_4px_0px_0px_#A3B18A] border-background-dark'
        case 'error': return 'bg-[#fee2e2] text-background-dark shadow-[4px_4px_0px_0px_#ef4444] border-background-dark border-l-[12px] border-l-red-500' // Highlighting error
        case 'warning': return 'bg-[#ffedd5] text-background-dark shadow-[4px_4px_0px_0px_#221f10] border-background-dark'
        default: return 'bg-white text-background-dark shadow-[4px_4px_0px_0px_#221f10] border-background-dark'
    }
})

const iconName = computed(() => {
    switch (props.variant) {
        case 'success': return 'check'
        case 'error': return 'error'
        case 'warning': return 'warning'
        default: return 'info'
    }
})

const iconClasses = computed(() => {
    switch (props.variant) {
        case 'success': return 'text-white'
        case 'error': return 'text-red-600'
        case 'warning': return 'text-orange-600'
        default: return 'text-primary'
    }
})

const role = computed(() => {
    return ['error', 'warning'].includes(props.variant) ? 'alert' : 'status'
})
</script>

<template>
    <Teleport to="body">
        <Transition enter-active-class="transform ease-out duration-300 transition"
            enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
            enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
            leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100"
            leave-to-class="opacity-0">
            <div v-if="modelValue" class="fixed z-[60] max-w-sm w-full pointer-events-auto" :class="positionClasses">
                <div class="w-full border-[3px] rounded-lg p-4 flex items-start gap-3" :class="variantClasses" :role="role">
                    <div v-if="variant === 'success'"
                        class="bg-sage text-background-dark p-1 rounded border-2 border-white flex items-center justify-center shrink-0">
                        <span class="material-symbols-outlined font-bold text-[20px]">{{ iconName }}</span>
                    </div>
                    <span v-else class="material-symbols-outlined text-[28px] shrink-0" :class="iconClasses">{{ iconName
                        }}</span>

                    <div class="flex-1 pt-0.5">
                        <h4 v-if="title" class="font-bold text-lg leading-tight">{{ title }}</h4>
                        <p v-if="message" class="text-sm font-medium opacity-90 mt-1">{{ message }}</p>
                        <slot />
                    </div>

                    <button @click="close" class="shrink-0 opacity-50 hover:opacity-100 transition-opacity" aria-label="Close notification">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>
