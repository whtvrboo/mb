<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue?: boolean
  label: string
  quantity?: number
  addedBy?: string
  note?: string
  checked?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  quantity: 1,
  checked: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'delete': []
}>()

const isChecked = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>

<template>
  <div 
    class="group relative flex flex-col gap-2 p-4 mb-4 border-[3px] border-background-dark rounded-lg transition-all active:translate-x-[2px] active:translate-y-[2px]"
    :class="[
      isChecked 
        ? 'bg-gray-50 border-gray-300 shadow-none opacity-60' 
        : 'bg-white shadow-neobrutalism active:shadow-neobrutalism-active'
    ]"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-start gap-3 flex-1">
        <!-- Neo Checkbox -->
        <label class="relative cursor-pointer mt-1 shrink-0">
          <input 
            type="checkbox" 
            v-model="isChecked"
            class="peer sr-only"
          />
          <div 
            class="size-6 border-2 border-background-dark rounded bg-white peer-checked:bg-primary transition-colors flex items-center justify-center"
            :class="{ 'border-gray-400 bg-gray-200 peer-checked:bg-gray-400': isChecked }"
          >
             <span class="material-symbols-outlined text-sm opacity-0 peer-checked:opacity-100 font-bold transition-opacity">check</span>
          </div>
        </label>

        <div class="flex flex-col">
          <span 
            class="text-xl font-bold leading-tight transition-colors"
            :class="[isChecked ? 'line-through decoration-2 decoration-background-dark text-gray-500' : 'group-hover:text-primary-dark']"
          >
            {{ label }}
          </span>
          <div v-if="!isChecked" class="flex items-center gap-2 mt-1">
            <span v-if="quantity > 1" class="text-xs font-bold border border-background-dark px-1.5 rounded bg-gray-100">
              Qty: {{ quantity }}
            </span>
            <span v-if="addedBy" class="text-xs text-gray-500 font-medium">
              Added by {{ addedBy }}
            </span>
          </div>
        </div>
      </div>

      <button 
        @click="$emit('delete')"
        class="opacity-0 group-hover:opacity-100 transition-opacity"
        :class="isChecked ? 'text-gray-400' : 'text-background-dark'"
      >
        <span class="material-symbols-outlined text-lg">delete</span>
      </button>
    </div>

    <!-- Note -->
    <div v-if="note && !isChecked" class="mt-2 pt-2 border-t-2 border-dashed border-gray-200">
      <p class="text-sm text-gray-600 italic">"{{ note }}"</p>
    </div>
  </div>
</template>
