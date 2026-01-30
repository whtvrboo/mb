<script setup lang="ts">
// Simple wrapper component for the Neobrutalist card style
</script>

<template>
  <div class="card bg-white border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism-lg overflow-hidden">
    <div v-if="$slots.header" class="mb-4">
      <slot name="header" />
    </div>
    
    <div class="card-body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="mt-4 pt-4 border-t-2 border-dashed border-gray-200">
      <slot name="footer" />
    </div>
  </div>
</template>
