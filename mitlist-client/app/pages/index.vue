<script setup lang="ts">
import confetti from 'canvas-confetti'

import { ref, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useChores } from '~/composables/useChores'
import type { UserResponse } from '~/types/auth'
import type { ChoreAssignmentWithChoreResponse } from '~/types/chores'

const { getMe } = useAuth()
// const { listItems } = useLists() // Could add bills here later
const { listAssignments, completeAssignment } = useChores()

const user = ref<UserResponse | null>(null)
const feedChores = ref<ChoreAssignmentWithChoreResponse[]>([])

const fetchData = async () => {
  try {
    const [userRes, choresRes] = await Promise.all([
      getMe(),
      listAssignments({ status_filter: 'pending' }) // Fetch pending chores
    ])
    user.value = userRes.data.value
    feedChores.value = choresRes.data.value?.slice(0, 3) || [] // Only show top 3
  } catch (e) {
    console.error('Failed to fetch dashboard data', e)
  }
}

onMounted(() => {
  fetchData()
})

const currentDate = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })

const completedChores = ref(new Set<number>())

const handleChoreChange = async (choreId: number) => {
  if (completedChores.value.has(choreId)) return

  // Optimistic update
  completedChores.value.add(choreId)

  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
  })

  try {
    await completeAssignment(choreId, { completed_at: new Date().toISOString() })

    // Wait for animation then remove from list
    setTimeout(() => {
      feedChores.value = feedChores.value.filter(c => c.id !== choreId)
      completedChores.value.delete(choreId) // Cleanup Set
    }, 500)
  } catch (e) {
    console.error('Failed to complete chore', e)
    completedChores.value.delete(choreId) // Revert state
  }
}
</script>

<template>
  <div
    class="bg-background-light dark:bg-background-dark min-h-screen text-background-dark dark:text-white font-display overflow-x-hidden pb-24">
    <!-- Header -->
    <header
      class="sticky top-0 z-50 bg-background-light border-b-[3px] border-background-dark px-5 h-20 flex items-center justify-between shadow-sm">
      <div class="flex flex-col">
        <h1 class="text-xl font-bold tracking-tight uppercase leading-none">My House</h1>
        <span class="text-sm font-medium opacity-60">{{ currentDate }}</span>
      </div>
      <div class="flex items-center gap-3">
        <div class="size-10 rounded-full border-[3px] border-background-dark overflow-hidden bg-gray-200">
          <img v-if="user?.avatar_url" :src="user.avatar_url" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center font-bold">{{ user?.name?.[0] ||
            '?' }}</div>
        </div>
        <button
          class="flex items-center justify-center size-10 rounded-lg hover:bg-black/5 transition-colors border-[3px] border-transparent hover:border-background-dark"
          aria-label="View notifications">
          <span class="material-symbols-outlined text-[28px]">notifications</span>
        </button>
      </div>
    </header>

    <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">
      <!-- House Status Card -->
      <section
        class="w-full bg-white border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism flex items-center gap-4">
        <div
          class="relative size-14 rounded-full bg-primary border-[3px] border-background-dark flex items-center justify-center shrink-0">
          <span class="material-symbols-outlined text-[28px]">bolt</span>
          <div class="absolute -top-1 -right-1 size-4 bg-[#e76f51] border-2 border-background-dark rounded-full"></div>
        </div>
        <div class="flex flex-col w-full">
          <div class="flex justify-between items-center mb-1">
            <h2 class="font-bold text-lg uppercase">House is Busy</h2>
            <span class="text-xs font-bold bg-background-dark text-white px-2 py-0.5 rounded">{{ feedChores.length }}
              Pending</span>
          </div>
          <div class="w-full h-3 bg-gray-200 rounded-full border-2 border-background-dark overflow-hidden">
            <div class="h-full w-1/3 bg-[#e76f51]"></div>
          </div>
        </div>
      </section>

      <!-- Feed Items -->
      <div v-if="feedChores.length === 0" class="text-center opacity-50 font-bold py-10">
        All caught up! Nothing to do.
      </div>

      <div v-for="chore in feedChores" :key="chore.id"
        class="relative w-full bg-primary border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism-lg flex flex-col gap-3 group hover:-translate-y-0.5 transition-transform">
        <div class="flex justify-between items-start">
          <div class="flex flex-col gap-2">
            <div
              class="bg-white/60 border-[2px] border-background-dark px-3 py-1 w-fit rounded-full text-xs font-bold uppercase flex items-center gap-1">
              <span class="material-symbols-outlined text-base">delete</span>
              Chore
            </div>
            <h3 class="text-2xl font-bold leading-tight mt-1">{{ chore.chore.name }}</h3>
            <!-- <p class="text-sm font-medium opacity-80">{{ chore.chore.description }}</p> -->
          </div>
          <label class="relative cursor-pointer">
            <input
              :checked="completedChores.has(chore.id)"
              class="peer sr-only"
              type="checkbox"
              :aria-label="`Mark ${chore.chore.name} as done`"
              @change="handleChoreChange(chore.id)" />
            <div
              class="size-12 bg-white border-[3px] border-background-dark rounded-xl shadow-[3px_3px_0px_0px_#221f10] peer-checked:shadow-none peer-checked:translate-x-1 peer-checked:translate-y-1 peer-checked:bg-green-500 transition-all flex items-center justify-center">
              <span
                class="material-symbols-outlined text-[28px] opacity-0 peer-checked:opacity-100 transition-opacity">check</span>
            </div>
          </label>
        </div>
        <div class="h-0.5 w-full bg-black/10 my-1"></div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <!-- <div class="size-8 rounded-full border-[2px] border-background-dark overflow-hidden bg-gray-200">
               <div class="w-full h-full bg-gray-300 flex items-center justify-center font-bold text-xs">You</div>
            </div> -->
            <span class="text-sm font-bold">Your Turn</span>
          </div>
          <span class="text-xs font-bold uppercase tracking-wide opacity-60">{{ chore.chore.points_value }} pts</span>
        </div>
      </div>

    </main>

    <!-- Bottom Nav -->
    <nav
      class="fixed bottom-0 left-0 w-full bg-white border-t-[3px] border-background-dark pb-6 pt-3 px-6 flex justify-between items-center z-50">
      <div class="flex flex-col items-center gap-1 text-primary">
        <div
          class="bg-primary border-[2px] border-background-dark p-2 rounded-lg -mt-6 shadow-neobrutalism transition-transform">
          <span class="material-symbols-outlined text-[28px] text-background-dark">home</span>
        </div>
        <span class="text-[10px] font-bold uppercase text-background-dark mt-1">Home</span>
      </div>

      <NuxtLink to="/lists"
        class="flex flex-col items-center gap-1 opacity-50 hover:opacity-100 transition-opacity cursor-pointer text-background-dark">
        <span class="material-symbols-outlined text-[28px]">list_alt</span>
        <span class="text-[10px] font-bold uppercase">Lists</span>
      </NuxtLink>

      <NuxtLink to="/chores"
        class="flex flex-col items-center gap-1 opacity-50 hover:opacity-100 transition-opacity cursor-pointer text-background-dark">
        <span class="material-symbols-outlined text-[28px]">check_box</span>
        <span class="text-[10px] font-bold uppercase">Chores</span>
      </NuxtLink>

      <NuxtLink to="/finance"
        class="flex flex-col items-center gap-1 opacity-50 hover:opacity-100 transition-opacity cursor-pointer text-background-dark">
        <span class="material-symbols-outlined text-[28px]">payments</span>
        <span class="text-[10px] font-bold uppercase">Expenses</span>
      </NuxtLink>
    </nav>
  </div>
</template>
