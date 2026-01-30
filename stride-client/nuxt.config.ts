// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    '@nuxt/a11y',
    '@nuxt/fonts',
    '@nuxt/eslint',
    '@nuxt/hints',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/test-utils',
    '@nuxt/ui'
  ],

  css: ['~/assets/css/main.css']
})