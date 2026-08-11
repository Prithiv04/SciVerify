PHASE 3 — SCIVERIFY USER AUTHENTICATION

We have successfully completed:

PHASE 1 — Project Foundation
PHASE 2 — Design System & Reusable UI Components

Phase 2 has been committed and pushed to Git.

The existing frontend contains:
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Supabase client foundation
- Zustand
- TanStack Query
- Axios
- React Hook Form
- Zod
- Lucide React
- Sonner
- Reusable UI components
- SciVerify-specific components
- /ui-preview showcase

The current "/" page is intentionally still a foundation placeholder.
Do NOT replace it with the final landing page.

==================================================
PHASE 3 OBJECTIVE
==================================================

Implement a complete, production-quality authentication system for SciVerify using Supabase Auth.

The authentication system must support:

1. User registration
2. User login
3. User logout
4. Persistent sessions
5. Forgot password
6. Password reset
7. Authentication state management
8. Protected routes
9. Auth loading states
10. Form validation
11. Error handling
12. Success notifications
13. Basic user profile handling
14. Database profile record
15. Row Level Security for profile data
16. A temporary authenticated placeholder page

The authentication implementation must be clean and ready for the future SciVerify backend.

==================================================
IMPORTANT SCOPE RESTRICTIONS
==================================================

THIS PHASE IS AUTHENTICATION ONLY.

DO NOT IMPLEMENT:

- Final landing page
- Real dashboard
- Citation verification
- Verification workflow
- AI agents
- LangGraph
- FastAPI integration
- Research APIs
- Crossref
- Semantic Scholar
- arXiv
- Verification history
- Benchmark system
- Agent progress system
- Evidence cards connected to real data

Do not unnecessarily modify Phase 1 or Phase 2 functionality.

The existing /ui-preview route MUST continue working.

==================================================
1. SUPABASE AUTHENTICATION
==================================================

Use Supabase Auth.

Use the existing Supabase client if one was created during Phase 1.

Do NOT create a second Supabase client.

Use environment variables:

VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY

If the project uses the newer Supabase publishable key naming, preserve the existing project convention rather than introducing duplicate variables.

Never hardcode Supabase credentials.

Never commit .env.

Make sure .env.example contains placeholder variable names only.

Example:

VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

==================================================
2. AUTHENTICATION PAGES
==================================================

Create these routes:

/login
/register
/forgot-password
/reset-password

Use the existing SciVerify design system from Phase 2.

Do NOT create a second UI system.

Reuse existing components such as:

Button
Input
Card
Badge
Spinner
Skeleton
Textarea where appropriate
Divider
etc.

The pages must be responsive.

==================================================
3. REGISTER PAGE
==================================================

Route:

/register

Fields:

- Full Name
- Email
- Password
- Confirm Password

Use React Hook Form + Zod.

Validation:

Full Name:
- required
- trimmed
- reasonable minimum length

Email:
- required
- valid email format

Password:
- required
- reasonable minimum length
- do not impose unnecessarily complicated password rules unless Supabase requires them

Confirm Password:
- required
- must match password

Show clear inline validation messages.

Example:

"Email address is invalid."

"Passwords do not match."

Do not expose raw Supabase errors directly to the user when a friendly message can be provided.

Submit flow:

Register
→ Validate form
→ Supabase signUp()
→ Handle response
→ Show appropriate success/error state

Handle both possible Supabase configurations:

A. Email confirmation disabled:
   Registration can immediately establish a session.

B. Email confirmation enabled:
   Tell the user that a confirmation email was sent and they need to verify their email.

Do not assume email confirmation is enabled or disabled.

After successful registration:

If a session exists:
→ redirect to the authenticated placeholder page.

If email confirmation is required:
→ show a clear "Check your email" state.

==================================================
4. LOGIN PAGE
==================================================

Route:

/login

Fields:

- Email
- Password

Use React Hook Form + Zod.

Include:

[ Sign In ]

Forgot password?

Don't have an account?
Create account

Login flow:

Submit
→ Validate
→ Supabase signInWithPassword()
→ Update auth state
→ Redirect to authenticated area

Preserve a redirect destination if a user was sent to login because they attempted to access a protected route.

Example:

User attempts:

/app/dashboard

Not authenticated
→ /login?redirect=/app/dashboard

After successful login:

→ /app/dashboard

If no redirect exists:

→ /app/home

==================================================
5. FORGOT PASSWORD
==================================================

Route:

/forgot-password

Field:

- Email

Use Supabase resetPasswordForEmail().

After submission:

Show a friendly confirmation:

"If an account exists for this email, you'll receive instructions to reset your password."

Do not reveal whether an email exists in the system.

Include a link back to Login.

==================================================
6. RESET PASSWORD
==================================================

Route:

/reset-password

The page must work with the recovery session established by Supabase.

Fields:

- New Password
- Confirm Password

Validate using Zod.

Use:

supabase.auth.updateUser({
  password: newPassword
})

After successful reset:

Show success state.

Provide:

[ Sign In ]

Do not automatically create confusing duplicate sessions.

Handle expired/invalid recovery sessions gracefully.

==================================================
7. AUTH STATE MANAGEMENT
==================================================

Create a clean authentication abstraction.

For example:

useAuth()

and/or:

AuthProvider

and/or:

authStore

Use whichever architecture best fits the existing Phase 1 structure.

Do NOT introduce multiple competing authentication state systems.

The auth state should expose at minimum:

- user
- session
- loading
- isAuthenticated
- signIn()
- signUp()
- signOut()
- resetPassword()

Use:

supabase.auth.onAuthStateChange()

to react to:

- SIGNED_IN
- SIGNED_OUT
- TOKEN_REFRESHED
- USER_UPDATED
- PASSWORD_RECOVERY

The Supabase client should handle session persistence.

Do NOT manually store passwords or authentication tokens in localStorage.

==================================================
8. SESSION PERSISTENCE
==================================================

The user should remain logged in after refreshing the browser.

Test:

Login
→ Dashboard/Auth placeholder
→ Refresh browser
→ User remains authenticated

Supabase should manage session persistence.

Do not implement custom token persistence unless absolutely necessary.

==================================================
9. AUTH GUARD
==================================================

Create a reusable protected-route/auth-guard component.

Protected route pattern:

/app/*

For example:

/app/home

Later this will contain:

/app/dashboard
/app/verify
/app/history
etc.

For this phase, only create:

/app/home

as a temporary authenticated placeholder.

If unauthenticated:

/app/home
→ redirect to /login

If authenticated:

/app/home
→ render authenticated placeholder.

While authentication state is still loading:

→ show a proper loading screen/spinner

Do NOT briefly show protected content before redirecting.

==================================================
10. TEMPORARY AUTHENTICATED HOME
==================================================

Create:

/app/home

This is NOT the real dashboard.

Display something simple and polished:

"Welcome to SciVerify"

"Authentication successful."

Show the authenticated user's:

- full name if available
- email

Include:

[ Logout ]

This page will be replaced by the real dashboard in a later phase.

Do not build dashboard statistics or verification functionality here.

==================================================
11. PROFILE DATABASE
==================================================

Create a Supabase database table:

profiles

Suggested schema:

id
user_id
full_name
avatar_url
created_at
updated_at

Recommended types:

id:
uuid primary key

user_id:
uuid referencing auth.users(id)

full_name:
text

avatar_url:
text nullable

created_at:
timestamptz default now()

updated_at:
timestamptz default now()

The profile should be associated with the authenticated Supabase user.

IMPORTANT:

Do not duplicate authentication credentials in profiles.

The auth.users table remains the source of truth for authentication.

The profiles table only stores application-level profile information.

==================================================
12. PROFILE CREATION
==================================================

When a user registers, their profile should be created.

Preferred approach:

Use a Supabase database trigger/function that creates a profile after a new auth.users record is created.

However, do not blindly create a trigger if the existing project already has an equivalent profile mechanism.

First inspect the existing project.

If no profile mechanism exists:

Create the required SQL migration for:

- profiles table
- profile creation trigger/function
- updated_at handling if appropriate

Store the registration full name in the profile.

A robust approach is to pass full_name through Supabase signup metadata:

data: {
  full_name: fullName
}

Then use that metadata when creating the profile.

Avoid race conditions where the frontend manually creates the profile immediately after signUp if a database trigger can handle it safely.

==================================================
13. ROW LEVEL SECURITY
==================================================

Enable RLS on profiles.

Users must only be able to:

SELECT their own profile.

UPDATE their own profile.

INSERT should normally be handled by the signup trigger rather than arbitrary client inserts.

Policies should use:

auth.uid() = user_id

Do NOT create a policy that allows every authenticated user to read every profile.

Do NOT disable RLS.

==================================================
14. PROFILE SERVICE
==================================================

Create a clean profile service abstraction.

For example:

src/services/profileService.ts

Functions could include:

getProfile()
updateProfile()

The UI should not contain raw Supabase database queries.

Keep database operations inside services.

==================================================
15. AUTH SERVICE
==================================================

Create or improve:

src/services/authService.ts

Keep Supabase authentication calls inside this service rather than scattering Supabase calls throughout components.

Potential functions:

signIn()
signUp()
signOut()
sendPasswordReset()
updatePassword()
getSession()
getUser()

Use strong TypeScript types.

==================================================
16. TYPES
==================================================

Create proper TypeScript types.

For example:

AuthUser
UserProfile
AuthState
LoginFormData
RegisterFormData
ForgotPasswordFormData
ResetPasswordFormData

Do not use "any" unnecessarily.

==================================================
17. ROUTING
==================================================

Update the existing router carefully.

Public routes:

/
/login
/register
/forgot-password
/reset-password
/ui-preview

Protected:

/app/*
/app/home

Do not break:

/ui-preview

The root "/" page must remain the current Phase 1 foundation page.

Do NOT replace it with the final landing page.

==================================================
18. AUTHENTICATED USER NAVIGATION
==================================================

The temporary /app/home page should include:

- User name
- User email
- Logout button

Logout should:

Supabase signOut()
→ clear auth state
→ redirect to /

Make sure browser back navigation cannot reveal protected content after logout.

==================================================
19. ERROR HANDLING
==================================================

Handle common cases:

Registration:
- email already registered
- invalid email
- weak password
- network failure
- email confirmation required

Login:
- incorrect credentials
- email not confirmed
- network failure
- rate limiting if returned

Password reset:
- invalid email
- network failure
- expired recovery session

Do not expose technical stack traces to users.

Use the existing Sonner/toast system where appropriate.

Inline errors should be used for form validation.

Toasts should be used for global success/error notifications.

==================================================
20. LOADING STATES
==================================================

Every auth action must have a loading state.

Examples:

Signing in...
Creating account...
Sending reset email...
Updating password...
Signing out...

Prevent duplicate submissions while requests are running.

Disable submit buttons during requests.

Use existing Spinner component.

==================================================
21. ACCESSIBILITY
==================================================

Make forms accessible.

Ensure:

- labels are associated with inputs
- keyboard navigation works
- focus states are visible
- buttons have meaningful text
- error messages are associated with fields
- color is not the only way to communicate state

==================================================
22. SECURITY REQUIREMENTS
==================================================

NEVER:

- store passwords
- log passwords
- expose service_role key in frontend
- put service_role key in .env variables beginning with VITE_
- hardcode secrets
- commit .env
- use service_role key from React
- store raw credentials in localStorage
- create insecure "isLoggedIn=true" flags as authentication

The frontend must only use the Supabase client-safe public key.

==================================================
23. ENVIRONMENT FILES
==================================================

Ensure:

.env

is ignored by Git.

Ensure:

.env.example

contains only placeholders.

Example:

VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

Do NOT put real credentials in .env.example.

==================================================
24. DO NOT BREAK PHASE 2
==================================================

The existing component system must continue to work.

Verify:

/ui-preview

still renders all existing components.

Do not rewrite the design system unnecessarily.

Use existing:

Button
Input
Card
Badge
Spinner
etc.

for authentication screens.

==================================================
25. VISUAL DESIGN
==================================================

Authentication pages should feel like SciVerify.

Use:

- dark background
- refined cards
- subtle borders
- existing primary accent
- professional typography
- restrained animation
- responsive layout

Example structure:

Logo
↓
Authentication Card
↓
Form
↓
Primary Action
↓
Secondary Navigation

Do not make the auth page visually complicated.

Desktop should have a polished centered layout.

Mobile should be comfortable and fully responsive.

==================================================
26. DATABASE MIGRATION
==================================================

If SQL migrations are part of the existing project structure:

Create a migration for profiles and RLS.

Do not execute destructive SQL.

Do not drop existing tables.

Do not modify unrelated database structures.

If Supabase CLI migrations are not currently configured, create the SQL migration file in a clearly documented location and explain exactly how it should be applied.

Do not pretend a database migration was executed if you cannot verify that it was executed.

==================================================
27. TESTING
==================================================

After implementation, run:

npm run lint

npm run build

Also run the development server.

Test manually:

TEST 1:
Open /

Expected:
Foundation page still works.

TEST 2:
Open /ui-preview

Expected:
UI preview still works.

TEST 3:
Open /register

Expected:
Registration page renders.

TEST 4:
Create a new account.

Expected:
Successful registration or email-confirmation state.

TEST 5:
Login with valid credentials.

Expected:
Redirect to /app/home.

TEST 6:
Refresh /app/home.

Expected:
Still authenticated.

TEST 7:
Open /app/home in a private/incognito browser without login.

Expected:
Redirect to /login.

TEST 8:
Logout.

Expected:
Redirect to /.

TEST 9:
After logout, manually open /app/home.

Expected:
Redirect to /login.

TEST 10:
Forgot password.

Expected:
Reset email flow works.

TEST 11:
Password reset.

Expected:
Password can be updated using Supabase recovery flow.

TEST 12:
Invalid login.

Expected:
Friendly error message.

TEST 13:
Invalid registration input.

Expected:
Zod validation messages.

TEST 14:
Check browser console.

Expected:
No authentication-related errors.

TEST 15:
Build.

Expected:
npm run build succeeds.

==================================================
28. DOCUMENTATION
==================================================

Update README only with information relevant to Phase 3.

Document:

- Supabase setup
- required environment variables
- how to configure authentication
- profile table
- RLS
- local development
- auth routes

Do not add fake backend documentation.

If a Supabase dashboard setting must be manually enabled, clearly document it.

==================================================
29. FINAL PROJECT STRUCTURE
==================================================

Keep the architecture clean.

A reasonable structure is:

src/
├── components/
│   ├── ui/
│   └── sciverify/
│
├── pages/
│   ├── UiPreviewPage.tsx
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── ForgotPasswordPage.tsx
│   ├── ResetPasswordPage.tsx
│   └── AuthHomePage.tsx
│
├── services/
│   ├── authService.ts
│   └── profileService.ts
│
├── hooks/
│   └── useAuth.ts
│
├── stores/
│   └── authStore.ts
│
├── routes/
│   ├── AppRouter.tsx
│   └── ProtectedRoute.tsx
│
├── lib/
│   └── supabase.ts
│
├── types/
│   └── auth.ts
│
└── ...

Adapt this to the existing project rather than blindly replacing its structure.

==================================================
30. IMPLEMENTATION RULE
==================================================

Work incrementally.

First inspect the existing Phase 1 and Phase 2 implementation.

Then:

1. Verify the existing Supabase client.
2. Verify the existing router.
3. Verify the existing design system.
4. Implement auth service.
5. Implement auth state management.
6. Implement profile database migration.
7. Implement RLS.
8. Implement Register.
9. Implement Login.
10. Implement Forgot Password.
11. Implement Reset Password.
12. Implement ProtectedRoute.
13. Implement /app/home.
14. Test the complete authentication flow.
15. Fix only Phase 3 issues.

Do not blindly overwrite existing files.

Prefer extending the existing architecture.

==================================================
31. FINAL ACCEPTANCE CRITERIA
==================================================

Phase 3 is complete ONLY when:

[ ] Register works
[ ] Login works
[ ] Logout works
[ ] Forgot password works
[ ] Reset password works
[ ] Sessions persist after refresh
[ ] Protected routes work
[ ] Unauthenticated users cannot access /app/*
[ ] Authenticated users can access /app/home
[ ] Profile is created for new users
[ ] User can read their own profile
[ ] RLS protects profile data
[ ] Auth errors are handled
[ ] Loading states work
[ ] Forms are validated
[ ] /ui-preview still works
[ ] "/" still shows the foundation page
[ ] No secrets are committed
[ ] npm run lint passes
[ ] npm run build passes
[ ] No TypeScript errors
[ ] No unnecessary changes to Phase 1/2
[ ] README contains Phase 3 setup instructions

==================================================
FINAL INSTRUCTION
==================================================

Implement ONLY Phase 3.

Do not proceed to Phase 4.

Do not build the landing page.

Do not build the dashboard.

Do not build verification functionality.

After completing the implementation, provide a concise summary containing:

1. Files created
2. Files modified
3. Supabase SQL migration created
4. Environment variables required
5. Routes added
6. Authentication flow implemented
7. Tests performed
8. npm run lint result
9. npm run build result
10. Any manual Supabase Dashboard steps still required

If anything cannot be verified, explicitly say so instead of claiming it works.