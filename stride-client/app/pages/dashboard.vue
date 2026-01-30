<script setup lang="ts">
// TODO: Add auth middleware when authentication is implemented
// definePageMeta({
//   middleware: 'auth',
// })

const user = ref(null)
const isLoading = ref(true)

// TODO: Fetch user data when auth is implemented
// onMounted(async () => {
//   try {
//     user.value = await $fetch('/api/v1/users/me')
//   } catch (err) {
//     await navigateTo('/login')
//   } finally {
//     isLoading.value = false
//   }
// })
onMounted(() => {
  isLoading.value = false
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Dashboard</h1>

    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <svg
        class="animate-spin h-8 w-8 text-gray-600 dark:text-gray-400"
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
    </div>

    <div v-else>
      <UiCard>
        <template #header>
          <h2 class="text-xl font-semibold">Welcome</h2>
        </template>

        <p class="text-gray-600 dark:text-gray-400">
          This is your dashboard. User data will be displayed here once authentication is implemented.
        </p>
      </UiCard>
    </div>
  </div>
</template>
