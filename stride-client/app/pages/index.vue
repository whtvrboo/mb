<script setup lang="ts">
// Mock Data for Dashboard
const feedItems = [
  { type: 'bill', title: 'Internet Bill', amount: '$89.99', subtitle: '/ Spectrum', urgent: true, dueLabel: 'Due Today at 5 PM' },
  { type: 'chore', title: 'Take Out Trash', subtitle: 'Bins to the curb, recycling sorted.', points: 20, assignedTo: 'You', completed: false },
]

const routineItems = [
  { title: 'Feed the Cat', subtitle: 'AM Kibble', type: 'Pet', icon: 'pets', completed: false },
  { title: 'Water Monstera', subtitle: 'Living Room', type: 'Plant', icon: 'potted_plant', completed: false },
]
</script>

<template>
  <div
    class="bg-background-light dark:bg-background-dark min-h-screen text-background-dark dark:text-white font-display overflow-x-hidden pb-24">
    <!-- Header -->
    <header
      class="sticky top-0 z-50 bg-background-light border-b-[3px] border-background-dark px-5 h-20 flex items-center justify-between shadow-sm">
      <div class="flex flex-col">
        <h1 class="text-xl font-bold tracking-tight uppercase leading-none">My House</h1>
        <span class="text-sm font-medium opacity-60">Tuesday, Oct 24</span>
      </div>
      <div class="flex items-center gap-3">
        <div class="size-10 rounded-full border-[3px] border-background-dark overflow-hidden bg-gray-200">
          <div class="w-full h-full bg-gray-300 flex items-center justify-center font-bold">You</div>
        </div>
        <button
          class="flex items-center justify-center size-10 rounded-lg hover:bg-black/5 transition-colors border-[3px] border-transparent hover:border-background-dark">
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
            <span class="text-xs font-bold bg-background-dark text-white px-2 py-0.5 rounded">4 Pending</span>
          </div>
          <div class="w-full h-3 bg-gray-200 rounded-full border-2 border-background-dark overflow-hidden">
            <div class="h-full w-1/3 bg-[#e76f51]"></div>
          </div>
        </div>
      </section>

      <!-- Feed Items -->
      <!-- Bill Item -->
      <div
        class="relative w-full bg-[#e76f51] border-[3px] border-background-dark rounded-xl shadow-neobrutalism-lg flex flex-col overflow-hidden group hover:-translate-y-1 transition-transform cursor-pointer">
        <div class="p-5 flex flex-col gap-4">
          <div class="flex justify-between items-start">
            <div
              class="bg-white/90 backdrop-blur border-[2px] border-background-dark px-3 py-1 rounded-full text-xs font-bold uppercase flex items-center gap-1 shadow-sm">
              <span class="material-symbols-outlined text-base">receipt_long</span>
              Bill Due
            </div>
            <div
              class="bg-background-dark text-white px-3 py-1 rounded-lg text-xs font-bold uppercase border border-white/20">
              Urgent
            </div>
          </div>
          <div class="flex flex-col gap-1 mt-1">
            <h3 class="text-3xl font-bold leading-none">Internet Bill</h3>
            <div class="flex items-baseline gap-2">
              <span class="text-4xl font-bold tracking-tight">$89.99</span>
              <span class="text-sm font-bold opacity-70">/ Spectrum</span>
            </div>
          </div>
        </div>
        <div class="bg-background-dark p-4 flex justify-between items-center text-white mt-auto">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-[#e76f51]">warning</span>
            <span class="text-sm font-bold">Due Today at 5 PM</span>
          </div>
          <button
            class="bg-white text-background-dark px-4 py-1.5 rounded-lg font-bold text-sm border-2 border-transparent hover:border-primary hover:bg-primary transition-all shadow-sm active:translate-y-0.5">
            Pay Now
          </button>
        </div>
      </div>

      <!-- Chore Item -->
      <div
        class="relative w-full bg-primary border-[3px] border-background-dark rounded-xl p-5 shadow-neobrutalism-lg flex flex-col gap-3 group hover:-translate-y-0.5 transition-transform">
        <div class="flex justify-between items-start">
          <div class="flex flex-col gap-2">
            <div
              class="bg-white/60 border-[2px] border-background-dark px-3 py-1 w-fit rounded-full text-xs font-bold uppercase flex items-center gap-1">
              <span class="material-symbols-outlined text-base">delete</span>
              Chore
            </div>
            <h3 class="text-2xl font-bold leading-tight mt-1">Take Out Trash</h3>
            <p class="text-sm font-medium opacity-80">Bins to the curb, recycling sorted.</p>
          </div>
          <label class="relative cursor-pointer">
            <input class="peer sr-only" type="checkbox" />
            <div
              class="size-12 bg-white border-[3px] border-background-dark rounded-xl shadow-[3px_3px_0px_0px_#221f10] peer-checked:shadow-none peer-checked:translate-x-1 peer-checked:translate-y-1 peer-checked:bg-sage transition-all flex items-center justify-center">
              <span
                class="material-symbols-outlined text-[28px] opacity-0 peer-checked:opacity-100 transition-opacity">check</span>
            </div>
          </label>
        </div>
        <div class="h-0.5 w-full bg-black/10 my-1"></div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="size-8 rounded-full border-[2px] border-background-dark overflow-hidden bg-gray-200">
              <div class="w-full h-full bg-gray-300 flex items-center justify-center font-bold text-xs">You</div>
            </div>
            <span class="text-sm font-bold">Your Turn</span>
          </div>
          <span class="text-xs font-bold uppercase tracking-wide opacity-60">Daily • 20pts</span>
        </div>
      </div>

      <!-- Routine Grid -->
      <div class="grid grid-cols-2 gap-4">
        <div
          class="bg-[#8E9DB3] border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism flex flex-col gap-3 h-full justify-between hover:-translate-y-0.5 transition-transform">
          <div class="flex flex-col gap-2">
            <div
              class="bg-white/60 border-[2px] border-background-dark px-2 py-0.5 w-fit rounded-md text-[10px] font-bold uppercase flex items-center gap-1">
              <span class="material-symbols-outlined text-sm">pets</span> Pet
            </div>
            <h3 class="text-xl font-bold leading-tight">Feed the Cat</h3>
          </div>
          <div class="flex items-center justify-between mt-2">
            <span class="text-xs font-bold opacity-70">AM Kibble</span>
            <button
              class="size-10 bg-white border-[2px] border-background-dark rounded-lg flex items-center justify-center shadow-[2px_2px_0px_0px_#221f10] active:translate-y-0.5 active:shadow-none">
              <span class="material-symbols-outlined text-lg">check</span>
            </button>
          </div>
        </div>

        <div
          class="bg-[#A3B18A] border-[3px] border-background-dark rounded-xl p-4 shadow-neobrutalism flex flex-col gap-3 h-full justify-between hover:-translate-y-0.5 transition-transform">
          <div class="flex flex-col gap-2">
            <div
              class="bg-white/60 border-[2px] border-background-dark px-2 py-0.5 w-fit rounded-md text-[10px] font-bold uppercase flex items-center gap-1">
              <span class="material-symbols-outlined text-sm">potted_plant</span> Plant
            </div>
            <h3 class="text-xl font-bold leading-tight">Water Monstera</h3>
          </div>
          <div class="flex items-center justify-between mt-2">
            <span class="text-xs font-bold opacity-70">Living Room</span>
            <button
              class="size-10 bg-white border-[2px] border-background-dark rounded-lg flex items-center justify-center shadow-[2px_2px_0px_0px_#221f10] active:translate-y-0.5 active:shadow-none">
              <span class="material-symbols-outlined text-lg">water_drop</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-center opacity-40 mt-4 gap-2">
        <span class="material-symbols-outlined">check_circle</span>
        <span class="font-bold text-sm">That's all for today!</span>
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
