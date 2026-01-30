<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const email = ref('')
const name = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)
const fieldErrors = ref<Record<string, string>>({})

function validateForm() {
  fieldErrors.value = {}

  if (!email.value) {
    fieldErrors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    fieldErrors.value.email = 'Please enter a valid email address'
  }

  if (!name.value) {
    fieldErrors.value.name = 'Name is required'
  } else if (name.value.length < 1 || name.value.length > 255) {
    fieldErrors.value.name = 'Name must be between 1 and 255 characters'
  }

  if (!password.value) {
    fieldErrors.value.password = 'Password is required'
  } else if (password.value.length < 8) {
    fieldErrors.value.password = 'Password must be at least 8 characters'
  }

  if (password.value !== confirmPassword.value) {
    fieldErrors.value.confirmPassword = 'Passwords do not match'
  }

  return Object.keys(fieldErrors.value).length === 0
}

async function handleRegister() {
  if (isLoading.value) return

  if (!validateForm()) {
    return
  }

  error.value = null
  isLoading.value = true

  try {
    // TODO: Replace with actual API call when auth endpoints are enabled
    const response = await $fetch('/api/v1/auth/register', {
      method: 'POST',
      body: {
        email: email.value,
        name: name.value,
        password: password.value,
        language_code: 'en',
      },
    })

    // TODO: Handle successful registration
    // Option 1: Auto-login and redirect to dashboard
    // Option 2: Show success message and redirect to login
    await navigateTo('/login')
  } catch (err: any) {
    if (err.status === 422) {
      // Map server validation errors to field errors
      if (err.data?.errors) {
        fieldErrors.value = { ...fieldErrors.value, ...err.data.errors }
      } else {
        error.value = 'Please check your input and try again'
      }
    } else if (err.status === 409) {
      error.value = 'An account with this email already exists'
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
      <h1 class="text-2xl font-bold text-center">Create Account</h1>
    </template>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <UiAlert
        v-if="error"
        variant="error"
        :title="error"
        class="mb-4"
      />

      <UiFormGroup
        label="Email"
        name="email"
        :error="fieldErrors.email"
        required
      >
        <UiInput
          v-model="email"
          type="email"
          placeholder="you@example.com"
          :disabled="isLoading"
          autocomplete="email"
          :error="!!fieldErrors.email"
        />
      </UiFormGroup>

      <UiFormGroup
        label="Name"
        name="name"
        :error="fieldErrors.name"
        required
      >
        <UiInput
          v-model="name"
          type="text"
          placeholder="Your name"
          :disabled="isLoading"
          autocomplete="name"
          :error="!!fieldErrors.name"
        />
      </UiFormGroup>

      <UiFormGroup
        label="Password"
        name="password"
        :error="fieldErrors.password"
        required
      >
        <UiInput
          v-model="password"
          type="password"
          placeholder="••••••••"
          :disabled="isLoading"
          autocomplete="new-password"
          :error="!!fieldErrors.password"
        />
      </UiFormGroup>

      <UiFormGroup
        label="Confirm Password"
        name="confirmPassword"
        :error="fieldErrors.confirmPassword"
        required
      >
        <UiInput
          v-model="confirmPassword"
          type="password"
          placeholder="••••••••"
          :disabled="isLoading"
          autocomplete="new-password"
          :error="!!fieldErrors.confirmPassword"
        />
      </UiFormGroup>

      <UiButton
        type="submit"
        block
        :loading="isLoading"
        :disabled="isLoading"
      >
        Create Account
      </UiButton>
    </form>

    <template #footer>
      <div class="text-center text-sm text-gray-600 dark:text-gray-400">
        Already have an account?
        <NuxtLink
          to="/login"
          class="text-blue-600 dark:text-blue-400 hover:underline font-medium"
        >
          Sign in
        </NuxtLink>
      </div>
    </template>
  </UiCard>
</template>
