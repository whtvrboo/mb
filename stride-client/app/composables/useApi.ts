import type { UseFetchOptions } from 'nuxt/app'

/**
 * Base API composable that wraps useFetch with the app's $api fetcher
 * (base URL, auth header, and error handling).
 */
export function useApi<T>(
  url: string | (() => string),
  options?: UseFetchOptions<T>,
) {
  const nuxtApp = useNuxtApp()
  return useFetch<T>(url, {
    ...options,
    $fetch: nuxtApp.$api as typeof $fetch,
  })
}
