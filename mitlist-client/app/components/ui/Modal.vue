<script setup lang="ts">
import { useId, onMounted, onUnmounted } from 'vue'

interface Props {
    modelValue: boolean
    title?: string
    width?: string
    closeable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    modelValue: false,
    title: '',
    width: 'max-w-lg',
    closeable: true,
})

const emit = defineEmits(['update:modelValue', 'close'])

const close = () => {
    if (props.closeable) {
        emit('update:modelValue', false)
        emit('close')
    }
}

const titleId = useId()

const onKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && props.modelValue) {
        close()
    }
}

onMounted(() => {
    window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
    <Teleport to="body">
        <Transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0"
            enter-to-class="opacity-100" leave-active-class="transition ease-in duration-150"
            leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="modelValue"
                class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background-dark/80 backdrop-blur-sm"
                role="dialog"
                aria-modal="true"
                :aria-labelledby="title ? titleId : undefined"
                @click="close">
                <div class="relative w-full bg-white border-[3px] border-background-dark rounded-xl shadow-[8px_8px_0px_0px_#221f10] overflow-hidden"
                    :class="[width]" @click.stop>
                    <!-- Header -->
                    <div v-if="title || closeable"
                        class="flex items-center justify-between px-6 py-4 border-b-[3px] border-background-dark bg-background-light">
                        <h3 v-if="title" :id="titleId" class="text-xl font-bold uppercase tracking-tight truncate">
                            {{ title }}
                        </h3>
                        <button v-if="closeable"
                            class="ml-auto flex items-center justify-center size-8 rounded-lg hover:bg-black/5 transition-colors"
                            aria-label="Close"
                            @click="close">
                            <span class="material-symbols-outlined font-bold">close</span>
                        </button>
                    </div>

                    <!-- Body -->
                    <div class="p-6">
                        <slot />
                    </div>

                    <!-- Footer -->
                    <div v-if="$slots.footer"
                        class="px-6 py-4 bg-gray-50 border-t-[3px] border-background-dark flex justify-end gap-3">
                        <slot name="footer" />
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>
