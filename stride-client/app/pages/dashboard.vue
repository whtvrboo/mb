<script setup lang="ts">
import type { UserResponse, GroupResponse } from '~/types/auth'

const { user: sessionUser, clear } = useUserSession()
const auth = useAuth()
const groupId = useCurrentGroupId()

// Fetch full user data from backend
const { data: user, error: userError, status: userStatus } = await auth.getMe()

// Fetch user's groups
const { data: groups, error: groupsError } = await auth.listGroups()

// Set current group if user has groups
if (groups.value && groups.value.length > 0 && !groupId.value) {
  groupId.value = groups.value[0].id
}

async function handleLogout() {
  await clear()
  await navigateTo('/login')
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Dashboard</h1>
      <UiButton @click="handleLogout" variant="outline">
        Sign Out
      </UiButton>
    </div>

    <div v-if="userStatus === 'pending'" class="flex justify-center items-center py-12">
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

    <div v-else-if="userError" class="space-y-4">
      <UiAlert variant="error" title="Failed to load user data">
        {{ userError }}
      </UiAlert>
    </div>

    <div v-else-if="user" class="space-y-6">
      <UiCard>
        <template #header>
          <h2 class="text-xl font-semibold">Welcome, {{ user.name }}</h2>
        </template>

        <div class="space-y-2">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            <span class="font-medium">Email:</span> {{ user.email }}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            <span class="font-medium">Language:</span> {{ user.language_code }}
          </p>
          <p v-if="user.last_login_at" class="text-sm text-gray-600 dark:text-gray-400">
            <span class="font-medium">Last login:</span> {{ new Date(user.last_login_at).toLocaleString() }}
          </p>
        </div>
      </UiCard>

      <UiCard v-if="groups && groups.length > 0">
        <template #header>
          <h2 class="text-xl font-semibold">Your Groups</h2>
        </template>

        <div class="space-y-2">
          <div
            v-for="group in groups"
            :key="group.id"
            class="p-3 border rounded-lg"
            :class="{ 'border-blue-500 bg-blue-50 dark:bg-blue-950': group.id === groupId }"
          >
            <div class="flex justify-between items-center">
              <div>
                <h3 class="font-medium">{{ group.name }}</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ group.timezone }} • {{ group.default_currency }}
                </p>
              </div>
              <UiButton
                v-if="group.id !== groupId"
                @click="groupId = group.id"
                size="sm"
                variant="outline"
              >
                Select
              </UiButton>
              <span v-else class="text-sm font-medium text-blue-600 dark:text-blue-400">
                Active
              </span>
            </div>
          </div>
        </div>
      </UiCard>

      <UiCard v-else>
        <template #header>
          <h2 class="text-xl font-semibold">No Groups</h2>
        </template>

        <p class="text-gray-600 dark:text-gray-400">
          You're not a member of any groups yet. Create or join a group to get started.
        </p>
      </UiCard>
    </div>
  </div>
</template>
