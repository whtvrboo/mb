# Stride Client (Mitlist Frontend)

Nuxt 4 frontend for the Mitlist household management application.

## Setup

1. **Install dependencies:**

   ```powershell
   npm install
   ```

2. **Configure environment:**

   ```powershell
   cp .env.example .env
   ```

   Then edit `.env` and set:
   - `NUXT_PUBLIC_API_BASE` - Backend API URL (e.g., `http://localhost:8000/api/v1`)
   - `NUXT_OAUTH_ZITADEL_CLIENT_ID` - Your Zitadel OAuth client ID
   - `NUXT_OAUTH_ZITADEL_CLIENT_SECRET` - Your Zitadel OAuth client secret
   - `NUXT_OAUTH_ZITADEL_SERVER_URL` - Your Zitadel instance URL
   - `NUXT_SESSION_PASSWORD` - Session encryption key (min 32 chars)

3. **Run development server:**
   ```powershell
   npm run dev
   ```

## Authentication

This app uses **Zitadel OIDC** for authentication:

1. User clicks "Sign in with Zitadel" on `/login`
2. Redirects to Zitadel for authentication
3. Zitadel redirects back to `/auth/zitadel` with authorization code
4. Server exchanges code for tokens and creates session
5. User is redirected to `/dashboard` with active session

The backend API expects a Bearer token (Zitadel access token) in the `Authorization` header.

## API Layer

The frontend has a complete TypeScript API layer:

- **Types** (`app/types/`) - TypeScript interfaces matching backend Pydantic schemas
- **Plugin** (`app/plugins/api.ts`) - Custom `$api` with auth headers and error handling
- **Composables** (`app/composables/`) - Module-specific API functions:
  - `useAuth()` - Users, groups, invites, locations, contacts
  - `useChores()` - Chores, assignments, templates, stats
  - `useFinance()` - Expenses, budgets, settlements, categories
  - `useLists()` - Lists, items, inventory
  - `useNotifications()` - Notifications, comments, reactions
  - `useGamification()` - Points, achievements, streaks, leaderboard
  - `useGovernance()` - Proposals, voting
  - `useRecipes()` - Recipes, meal plans
  - `usePets()` - Pet care, medical records, schedules
  - `usePlants()` - Plant care, species, schedules
  - `useAssets()` - Home assets, maintenance, insurance
  - `useDocuments()` - Document storage, credentials
  - `useAudit()` - Audit logs, reports, tags
  - `useCalendar()` - Calendar feed

## Project Structure

```
stride-client/
├── app/
│   ├── components/      # Vue components
│   ├── composables/     # API composables
│   ├── layouts/         # Page layouts
│   ├── middleware/      # Route middleware (auth)
│   ├── pages/           # File-based routes
│   ├── plugins/         # Nuxt plugins (API)
│   └── types/           # TypeScript types
├── server/
│   └── routes/          # Server routes (OAuth callback)
└── nuxt.config.ts       # Nuxt configuration
```

## Development

- **Dev server:** `npm run dev` (http://localhost:3000)
- **Build:** `npm run build`
- **Preview:** `npm run preview`

## Next Steps

1. ✅ Auth flow with Zitadel OIDC
2. ✅ Dashboard with user info and group selection
3. 🔄 Feature pages (lists, chores, finance, etc.)
4. 🔄 Error handling UX (toasts/alerts)
5. 🔄 Loading states and optimistic updates
