export default defineNuxtPlugin(async (nuxtApp) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string
  
  // Get session from nuxt-auth-utils
  const { data: session } = await useFetch('/api/_auth/session')
  const tokenState = useState<string | null>('api-token', () => session.value?.accessToken || null)

  const api = $fetch.create({
    baseURL: apiBase,
    onRequest({ options }) {
      const token = tokenState.value
      if (token) {
        options.headers = options.headers || new Headers()
        const headers = options.headers as Headers
        headers.set('Authorization', `Bearer ${token}`)
      }
      const groupId = useState<number | null>('current-group-id', () => null).value
      if (groupId != null) {
        options.headers = options.headers || new Headers()
        const headers = options.headers as Headers
        headers.set('X-Group-Id', String(groupId))
      }
    },
    async onResponseError({ response }) {
      if (response.status === 401) {
        await nuxtApp.runWithContext(() => {
          navigateTo('/login')
        })
      }
    },
  })

  return {
    provide: {
      api,
    },
  }
})

declare module '#app' {
  interface NuxtApp {
    $api: typeof $fetch
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $api: typeof $fetch
  }
}
