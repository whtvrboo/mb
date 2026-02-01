/**
 * Dev-only: sign in as test user without Zitadel.
 * Sets session with Bearer dev:test@test.local; backend must have DEV_TEST_USER_ENABLED=true.
 * setUserSession is auto-imported by nuxt-auth-utils.
 */
import { sendRedirect } from 'h3'

const DEV_TOKEN = 'dev:test@test.local'
const DEV_USER = {
  id: 'dev-test',
  email: 'test@test.local',
  name: 'Test User',
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  if (!config.public.devAuth) {
    return sendRedirect(event, '/login?error=dev_auth_disabled', 302)
  }
  await setUserSession(event, {
    user: DEV_USER,
    accessToken: DEV_TOKEN,
  })
  return sendRedirect(event, '/dashboard')
})
