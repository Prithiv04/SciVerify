# SciVerify

Multi-Agent Scientific Citation Verification System

## Frontend

The React frontend lives in `frontend/`.

```bash
cd frontend
npm install
npm run dev
```

## Phase 3 — Authentication (Supabase)

SciVerify uses [Supabase Auth](https://supabase.com/docs/guides/auth) for registration, login, logout, password reset, and session persistence.

### Environment variables

Copy the example file and fill in your Supabase project values:

```bash
cd frontend
cp .env.example .env
```

Required variables:

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

Use the **Project URL** and **anon/public** key from Supabase Dashboard → Project Settings → API.

Never commit `.env`. Never expose the `service_role` key in frontend code or any `VITE_` variable.

### Database migration (profiles + RLS)

Apply the SQL migration to create the `profiles` table, signup trigger, and Row Level Security policies:

**File:** `supabase/migrations/001_create_profiles.sql`

**Option A — Supabase Dashboard**

1. Open Supabase Dashboard → SQL Editor
2. Paste the migration SQL
3. Run the query

**Option B — Supabase CLI**

```bash
supabase link --project-ref <your-project-ref>
supabase db push
```

The migration creates:

- `public.profiles` linked to `auth.users`
- A trigger that inserts a profile on signup using `full_name` from signup metadata
- RLS policies so users can only **select** and **update** their own profile

### Supabase Dashboard settings

Configure these manually in Supabase Dashboard → Authentication:

1. **Site URL:** `http://localhost:5173` (local dev)
2. **Redirect URLs:** add `http://localhost:5173/reset-password`
3. **Email confirmation:** optional — the app handles both enabled and disabled flows
4. **Email templates:** customize confirmation/reset emails if desired

For production, add your deployed domain to Site URL and Redirect URLs.

### Auth routes

| Route | Access |
|-------|--------|
| `/` | Public — foundation placeholder |
| `/ui-preview` | Public — design system showcase |
| `/login` | Guest only |
| `/register` | Guest only |
| `/forgot-password` | Public |
| `/reset-password` | Recovery session |
| `/app/home` | Protected — temporary authenticated placeholder |

### Authentication flow

1. **Register** → `signUp()` with `full_name` metadata → profile created by DB trigger
2. **Login** → `signInWithPassword()` → redirect to `/app/home` (or `?redirect=` target)
3. **Logout** → `signOut()` → redirect to `/`
4. **Forgot password** → `resetPasswordForEmail()` → email with link to `/reset-password`
5. **Reset password** → `updateUser({ password })` → sign out → sign in with new password

Sessions persist via Supabase client storage (browser refresh keeps the user signed in).

### Local development scripts

```bash
npm run dev      # start Vite dev server
npm run lint     # ESLint
npm run build    # typecheck + production build
```

## License

MIT
