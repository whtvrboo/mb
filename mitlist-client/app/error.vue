<template>
  <UContainer class="min-h-screen flex items-center justify-center">
    <UCard>
      <template #header>
        <h1 class="text-4xl font-bold">{{ error.statusCode }}</h1>
      </template>
      <p>{{ error.statusMessage }}</p>
      <template #footer>
        <UButton @click="handleError">Go Home</UButton>
      </template>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
const props = defineProps<{
  error: {
    statusCode: number
    statusMessage: string
  }
}>()

const handleError = () => clearError({ redirect: '/' })
</script>
