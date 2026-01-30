export default defineNuxtRouteMiddleware(async (to) => {
  // Public routes that don't require auth
  const publicRoutes = ['/login', '/register']
  
  if (publicRoutes.includes(to.path)) {
    return
  }

  // Check if user has a session
  const { loggedIn } = useUserSession()
  
  if (!loggedIn.value) {
    return navigateTo('/login')
  }
})
