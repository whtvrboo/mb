<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const email = ref('')
const password = ref('')
const showPassword = ref(false)

const handleZitadelLogin = () => {
  window.location.href = '/auth/zitadel'
}

const handleZitadelRegister = () => {
  window.location.href = '/auth/zitadel/register'
}
</script>

<template>
  <div
    class="bg-background-light text-background-dark font-display min-h-screen flex flex-col relative overflow-x-hidden selection:bg-primary selection:text-background-dark">
    <!-- Decorative Shape - Different rotation/pos than register -->
    <div class="absolute top-[-80px] left-[-60px] opacity-5 pointer-events-none z-0 -rotate-12">
      <svg fill="none" height="300" viewBox="0 0 200 200" width="300" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="80" stroke="#221f10" stroke-width="8"></circle>
        <path d="M100 20L100 180M20 100L180 100" stroke="#221f10" stroke-width="8"></path>
      </svg>
    </div>

    <!-- Header -->
    <header class="relative z-10 px-6 pt-8 pb-2 flex items-center justify-between">
      <NuxtLink to="/"
        class="flex items-center justify-center size-12 bg-white border-[3px] border-background-dark rounded-xl shadow-neobrutalism-sm active:translate-x-0.5 active:translate-y-0.5 active:shadow-none transition-all group">
        <span
          class="material-symbols-outlined text-[24px] group-hover:-translate-x-0.5 transition-transform">home</span>
      </NuxtLink>
    </header>

    <main class="flex-1 px-6 pt-4 pb-8 flex flex-col relative z-10 w-full max-w-md mx-auto">
      <!-- Title Section -->
      <div class="flex items-end justify-between mb-8 mt-2">
        <div class="flex flex-col gap-1 z-10">
          <h1 class="text-[40px] font-bold leading-[0.9] tracking-tight">Welcome<br />Back</h1>
          <p class="text-sm font-bold opacity-60 mt-2 max-w-[200px]">Sign in to continue your journey.</p>
        </div>
        <!-- Key Icon Graphic -->
        <div class="relative w-24 h-24 mb-1 shrink-0 -mr-2">
          <svg class="w-full h-full drop-shadow-[4px_4px_0px_rgba(34,31,16,1)]" fill="none" viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="40" r="20" fill="#eecd2b" stroke="#221f10" stroke-width="3"></circle>
            <circle cx="50" cy="40" r="8" fill="#221f10"></circle>
            <path d="M50 60V90H30V75H50" stroke="#221f10" stroke-width="6" stroke-linecap="round"
              stroke-linejoin="round"></path>
          </svg>
        </div>
      </div>

      <!-- Form -->
      <form class="flex flex-col gap-5 w-full" @submit.prevent>
        <div class="flex flex-col gap-1.5 group">
          <label
            class="font-bold text-sm uppercase ml-1 flex items-center gap-1 group-focus-within:text-primary transition-colors duration-300">
            Email Address
          </label>
          <div class="relative">
            <input v-model="email"
              class="w-full h-14 bg-white border-[3px] border-background-dark rounded-xl px-4 text-lg font-bold placeholder:text-gray-300 placeholder:font-medium focus:ring-0 focus:border-primary focus:outline-none shadow-neobrutalism transition-all"
              placeholder="hello@mitlist.com" type="email" />
            <span
              class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none group-focus-within:text-primary transition-colors">mail</span>
          </div>
        </div>

        <div class="flex flex-col gap-1.5 group">
          <label
            class="font-bold text-sm uppercase ml-1 flex items-center gap-1 group-focus-within:text-primary transition-colors duration-300">
            Password
          </label>
          <div class="relative">
            <input v-model="password" :type="showPassword ? 'text' : 'password'"
              class="w-full h-14 bg-white border-[3px] border-background-dark rounded-xl px-4 text-lg font-bold placeholder:text-gray-300 placeholder:font-medium focus:ring-0 focus:border-primary focus:outline-none shadow-neobrutalism transition-all"
              placeholder="••••••••" />
            <button type="button" @click="showPassword = !showPassword"
              class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-background-dark transition-colors outline-none">
              <span class="material-symbols-outlined text-[22px]">{{ showPassword ? 'visibility' : 'visibility_off'
              }}</span>
            </button>
          </div>
          <div class="flex justify-end">
            <a href="#" class="text-xs font-bold uppercase hover:text-primary transition-colors">Forgot Pwd?</a>
          </div>
        </div>

        <div class="h-2"></div>

        <button
          class="group relative w-full h-[72px] bg-[#221f10] text-white border-[3px] border-background-dark rounded-xl shadow-neobrutalism-lg active:translate-x-1 active:translate-y-1 active:shadow-none transition-all flex items-center justify-center overflow-hidden">
          <div class="absolute top-2 left-2 right-2 h-[3px] bg-white/10 rounded-full"></div>
          <span class="relative font-black text-xl uppercase tracking-wider flex items-center gap-3">
            Log In
            <div class="bg-white text-background-dark rounded-full p-1 group-hover:translate-x-1 transition-transform">
              <span class="material-symbols-outlined text-[20px] block font-bold">arrow_forward</span>
            </div>
          </span>
        </button>
      </form>

      <div class="relative py-8 flex items-center justify-center">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t-[3px] border-dashed border-background-dark/20"></div>
        </div>
        <div
          class="relative bg-background-light px-4 font-bold text-sm text-background-dark/50 uppercase tracking-widest">
          or</div>
      </div>

      <button @click="handleZitadelLogin"
        class="group w-full bg-white border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism flex items-center justify-between active:translate-x-[2px] active:translate-y-[2px] active:shadow-neobrutalism-sm transition-all text-left relative">
        <span class="font-bold text-lg">Sign in with Zitadel</span>
        <span class="material-symbols-outlined text-2xl">lock</span>
      </button>

      <button @click="handleZitadelRegister"
        class="group w-full bg-primary border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism flex items-center justify-between active:translate-x-[2px] active:translate-y-[2px] active:shadow-neobrutalism-sm transition-all text-left relative">
        <span class="font-bold text-lg text-background-dark">Sign up with Zitadel</span>
        <span class="material-symbols-outlined text-2xl text-background-dark">person_add</span>
      </button>

      <div class="mt-auto pt-8 mb-2 text-center">
        <p class="text-sm font-bold text-background-dark/70">
          New here? Use “Sign up with Zitadel” above to create an account.
        </p>
      </div>
    </main>
  </div>
</template>
