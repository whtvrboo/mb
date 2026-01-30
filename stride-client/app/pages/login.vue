<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const route = useRoute()
const error = ref<string | null>(null)

// Check for error from OAuth callback
if (route.query.error === 'auth_failed') {
  error.value = 'Authentication failed. Please try again.'
}

function handleZitadelLogin() {
  // Redirect to Zitadel OAuth flow
  window.location.href = '/auth/zitadel'
}
</script>

<template>
  <UiCard>
    <template #header>
      <h1 class="text-2xl font-bold text-center">Sign In</h1>
    </template>

    <div class="space-y-4">
      <UiAlert
        v-if="error"
        variant="error"
        :title="error"
        class="mb-4"
      />

      <UiButton
        type="button"
        block
        @click="handleZitadelLogin"
      >
        Sign in with Zitadel
      </UiButton>

      <p class="text-sm text-center text-gray-600 dark:text-gray-400">
        Authentication is handled via Zitadel OIDC
      </p>
    </div>

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
