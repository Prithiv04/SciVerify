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

## Phase 20 — Universal Legal Retrieval

SciVerify implements a **universal, legally compliant full-text retrieval pipeline** designed to give any scientific DOI the maximum possible chance of being retrieved from a freely accessible source — without ever bypassing paywalls, Cloudflare protections, CAPTCHAs, authentication walls, or any anti-bot measures.

### Source Hierarchy (Tier 0 → Tier 6)

When a DOI is submitted, the pipeline queries **all permitted sources in parallel** and then attempts candidates in strict tier order:

| Tier | Source | Type |
|------|--------|------|
| 0 | **PMC PDF** (`pmc.ncbi.nlm.nih.gov`) | NIH Open Access — authoritative |
| 1 | **Europe PMC HTML / PMC HTML** (`europepmc.org`, `ncbi.nlm.nih.gov/pmc`) | OA repository |
| 2 | **OA Repository PDF** (arXiv, Unpaywall repository, Zenodo, bioRxiv, etc.) | OA repository |
| 3 | **OA Repository HTML** (same sources, HTML format) | OA repository |
| 4 | **Semantic Scholar OA PDF** (mixed provenance, public graph API) | Mixed OA |
| 5 | **Publisher OA PDF** (legitimate open-access publisher PDFs only) | Publisher OA |
| 6 | **Publisher OA HTML** (OA publisher landing pages) | Publisher OA |

### Discovery Sources

The pipeline queries four external APIs for each request:

1. **Europe PMC REST** (`ebi.ac.uk/europepmc`) — finds PMCID from DOI; yields Tier 0/1 candidates.
2. **OpenAlex** (`api.openalex.org`) — OA locations from the paper graph.
3. **Unpaywall** (`api.unpaywall.org`) — OA location catalogue (repository vs publisher classified separately).
4. **Semantic Scholar Graph API** (`api.semanticscholar.org`) — OA PDF URL when `isOpenAccess=true`.

All sources are queried unconditionally and their candidates are merged, deduplicated (by URL), and ranked before any download is attempted.

### Legal Boundaries

- **No paywall bypass.** The downloader actively rejects paywalled and subscription-required HTML using keyword detection (`is_paywall_content`).
- **No anti-bot bypass.** Cloudflare challenges, CAPTCHAs, and interstitial pages are detected and the candidate is skipped (`is_interstitial_content`).
- **No authentication.** Only unauthenticated, publicly accessible URLs are attempted.
- **No secrets in URLs.** All discovery API calls are unauthenticated or use a generic contact email (Unpaywall). No API keys are stored in URLs.

### Failure Handling

If no candidate succeeds, the pipeline returns `FULL_TEXT_UNAVAILABLE` with the full list of attempted URLs and the specific rejection reason for each candidate. The frontend distinguishes between:

- **Citation not found** (DOI does not resolve) → HTTP 404 → "The cited paper could not be found. Please check the DOI."
- **Citation found, full text unavailable** (DOI resolved, but no accessible source) → HTTP 503 → "Citation found, but the full text could not be retrieved from any permitted open-access source."

### Test Coverage

Phase 20 deterministic tests live in `backend/app/tests/test_universal_retrieval.py` (41 tests):

- Europe PMC / PMC discovery (PMCID resolution, prefix normalisation, error handling)
- Unpaywall discovery (repository vs publisher classification, PDF vs landing page policy)
- Semantic Scholar discovery (OA PDF, source type classification, error handling)
- 6-tier candidate ranking and sort order
- URL deduplication across sources
- Full fallback hierarchy integration tests
- DOI_NOT_FOUND vs FULL_TEXT_UNAVAILABLE distinction
- Security: no secrets in discovery request URLs
- Access control: paywall and interstitial candidates are rejected

## License

MIT
