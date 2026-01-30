<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)

async function handleLogin() {
  if (isLoading.value) return

  error.value = null
  isLoading.value = true

  try {
    // TODO: Replace with actual API call when auth endpoints are enabled
    // For now, this is a placeholder structure
    const response = await $fetch('/api/v1/auth/login', {
      method: 'POST',
      body: {
        email: email.value,
        password: password.value,
      },
    })

    // TODO: Store token and user data
    // await navigateTo('/dashboard')
  } catch (err: any) {
    if (err.status === 401) {
      error.value = 'Invalid email or password'
    } else if (err.status === 422) {
      error.value = 'Please check your input and try again'
    } else {
      error.value = 'An error occurred. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <UiCard>
    <template #header>
      <h1 class="text-2xl font-bold text-center">Sign In</h1>
    </template>

    <form @submit.prevent="handleLogin" class="space-y-4">
      <UiAlert
        v-if="error"
        variant="error"
        :title="error"
        class="mb-4"
      />

      <UiFormGroup label="Email" name="email" required>
        <UiInput
          v-model="email"
          type="email"
          placeholder="you@example.com"
          :disabled="isLoading"
          autocomplete="email"
        />
      </UiFormGroup>

      <UiFormGroup label="Password" name="password" required>
        <UiInput
          v-model="password"
          type="password"
          placeholder="••••••••"
          :disabled="isLoading"
          autocomplete="current-password"
        />
      </UiFormGroup>

      <UiButton
        type="submit"
        block
        :loading="isLoading"
        :disabled="isLoading"
      >
        Sign In
      </UiButton>
    </form>

    <template #footer>
      <div class="text-center text-sm text-gray-600 dark:text-gray-400">
        Don't have an account?
        <NuxtLink
          to="/register"
          class="text-blue-600 dark:text-blue-400 hover:underline font-medium"
        >
          Sign up
        </NuxtLink>
      </div>
    </template>
  </UiCard>
</template>
