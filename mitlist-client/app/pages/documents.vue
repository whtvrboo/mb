<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useDocuments } from "~/composables/useDocuments";
import type {
  DocumentResponse,
  SharedCredentialResponse,
  SharedCredentialWithPasswordResponse,
} from "~/types/documents";

const { listDocuments, listCredentials, revealCredential } = useDocuments();

const activeTab = ref<"files" | "secrets">("files");
const docs = ref<DocumentResponse[]>([]);
const secrets = ref<SharedCredentialResponse[]>([]);
const isLoading = ref(true);

const fetchData = async () => {
  isLoading.value = true;
  try {
    const [docsData, secretsData] = await Promise.all([
      listDocuments(),
      listCredentials(),
    ]);
    docs.value = docsData;
    secrets.value = secretsData;
  } catch (e) {
    console.error("Failed to fetch documents", e);
  } finally {
    isLoading.value = false;
  }
};

const handleReveal = async (secret: SharedCredentialResponse) => {
  try {
    const revealed = await revealCredential(secret.id);
    alert(`Password: ${revealed.credential_value}`); // Placeholder for better UI modal
  } catch (e) {
    console.error("Failed to reveal", e);
  }
};

onMounted(() => {
  fetchData();
});
</script>

<template>
  <div
    class="bg-background-light dark:bg-background-dark min-h-screen text-background-dark font-display pb-24"
  >
    <header
      class="sticky top-0 z-50 bg-background-light border-b-[3px] border-background-dark px-5 h-16 flex items-center justify-between shadow-sm"
    >
      <div class="flex items-center gap-3">
        <NuxtLink
          to="/"
          aria-label="Go back"
          class="flex items-center justify-center size-10 rounded-lg border-[2px] border-transparent hover:border-background-dark hover:bg-black/5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-background-dark"
        >
          <span class="material-symbols-outlined text-[28px]" aria-hidden="true"
            >arrow_back</span
          >
        </NuxtLink>
      </div>
      <h1 class="text-xl font-bold tracking-tight uppercase">Documents</h1>
      <div class="size-10 flex items-center justify-end">
        <span class="material-symbols-outlined text-[24px]" aria-hidden="true"
          >upload_file</span
        >
      </div>
    </header>

    <main class="flex flex-col gap-6 p-5 max-w-lg mx-auto w-full">
      <!-- Tabs -->
      <div
        role="tablist"
        aria-label="Document Types"
        class="flex bg-white border-[3px] border-background-dark rounded-xl overflow-hidden shadow-neobrutalism-sm"
      >
        <button
          @click="activeTab = 'files'"
          role="tab"
          :aria-selected="activeTab === 'files'"
          class="flex-1 py-3 font-bold uppercase transition-colors focus-visible:outline-none focus-visible:bg-gray-100 focus-visible:ring-2 focus-visible:ring-background-dark focus-visible:z-10"
          :class="
            activeTab === 'files'
              ? 'bg-primary text-background-dark'
              : 'hover:bg-gray-100'
          "
        >
          Files
        </button>
        <div class="w-[3px] bg-background-dark"></div>
        <button
          @click="activeTab = 'secrets'"
          role="tab"
          :aria-selected="activeTab === 'secrets'"
          class="flex-1 py-3 font-bold uppercase transition-colors focus-visible:outline-none focus-visible:bg-gray-100 focus-visible:ring-2 focus-visible:ring-background-dark focus-visible:z-10"
          :class="
            activeTab === 'secrets'
              ? 'bg-primary text-background-dark'
              : 'hover:bg-gray-100'
          "
        >
          Secrets
        </button>
      </div>

      <div
        v-if="isLoading"
        aria-busy="true"
        class="text-center py-10 opacity-50"
      >
        Loading...
      </div>

      <!-- Files List -->
      <div
        v-if="activeTab === 'files' && !isLoading"
        role="tabpanel"
        aria-label="Files"
        class="flex flex-col gap-3"
      >
        <div
          v-if="docs.length === 0"
          class="text-center py-10 opacity-50 font-bold"
        >
          No documents.
        </div>

        <div
          v-for="doc in docs"
          :key="doc.id"
          class="bg-white border-[3px] border-background-dark rounded-xl p-4 flex items-center justify-between shadow-sm hover:translate-x-1 transition-transform cursor-pointer"
        >
          <div class="flex items-center gap-3">
            <span
              class="material-symbols-outlined text-4xl text-gray-400"
              aria-hidden="true"
              >description</span
            >
            <div class="flex flex-col">
              <h3 class="font-bold text-lg leading-tight">{{ doc.title }}</h3>
              <span class="text-xs font-medium opacity-60 uppercase">{{
                doc.category || "General"
              }}</span>
            </div>
          </div>
          <span class="material-symbols-outlined" aria-hidden="true"
            >download</span
          >
        </div>
      </div>

      <!-- Secrets List -->
      <div
        v-if="activeTab === 'secrets' && !isLoading"
        role="tabpanel"
        aria-label="Secrets"
        class="flex flex-col gap-3"
      >
        <div
          v-if="secrets.length === 0"
          class="text-center py-10 opacity-50 font-bold"
        >
          No shared secrets.
        </div>

        <div
          v-for="secret in secrets"
          :key="secret.id"
          class="bg-background-dark text-white border-[3px] border-background-dark rounded-xl p-4 flex items-center justify-between shadow-[4px_4px_0px_0px_#8E9DB3]"
        >
          <div class="flex items-center gap-3">
            <span
              class="material-symbols-outlined text-4xl text-primary"
              aria-hidden="true"
              >key</span
            >
            <div class="flex flex-col">
              <h3 class="font-bold text-lg leading-tight">{{ secret.name }}</h3>
              <span class="text-xs font-bold opacity-60 uppercase">{{
                secret.url || "Credential"
              }}</span>
            </div>
          </div>
          <button
            @click="handleReveal(secret)"
            aria-label="Reveal password"
            class="bg-white text-background-dark size-10 rounded border border-background-dark flex items-center justify-center hover:bg-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-background-dark focus-visible:ring-offset-2"
          >
            <span class="material-symbols-outlined" aria-hidden="true"
              >visibility</span
            >
          </button>
        </div>
      </div>
    </main>
  </div>
</template>
