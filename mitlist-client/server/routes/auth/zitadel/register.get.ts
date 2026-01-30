import { getRequestURL } from 'h3'

/**
 * Redirects to Zitadel's authorization endpoint with prompt=create
 * so users see the registration form instead of login.
 * Callback is the same as login: /auth/zitadel
 */
export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const { clientId, serverUrl } = config.oauth?.zitadel ?? {}

  if (!clientId || !serverUrl) {
    return sendRedirect(event, '/register?error=config')
  }

  const requestURL = getRequestURL(event)
  const redirectUri = `${requestURL.origin}/auth/zitadel`

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: 'openid profile email',
    prompt: 'create',
  })

  const authorizeUrl = `${serverUrl.replace(/\/$/, '')}/oauth/v2/authorize?${params.toString()}`
  return sendRedirect(event, authorizeUrl)
})
