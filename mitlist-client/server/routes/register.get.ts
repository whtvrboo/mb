/**
 * Redirect /register to login. Sign-up is done via Zitadel; use "Create Account" on login
 * which goes to /auth/zitadel/register.
 */
export default defineEventHandler((event) => {
  return sendRedirect(event, '/login')
})
