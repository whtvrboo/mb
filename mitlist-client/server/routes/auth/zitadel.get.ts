export default defineOAuthZitadelEventHandler({
  async onSuccess(event, { user, tokens }) {
    await setUserSession(event, {
      user: {
        id: user.sub,
        email: user.email || `${user.sub}@zitadel.local`,
        name: user.name || user.preferred_username || user.email || 'User',
      },
      accessToken: tokens.access_token,
    })
    return sendRedirect(event, '/dashboard')
  },
  onError(event, error) {
    console.error('Zitadel OAuth error:', error)
    return sendRedirect(event, '/login?error=auth_failed')
  },
})
