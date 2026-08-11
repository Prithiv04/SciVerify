PHASE 1 — Project Foundation
Goal

Create a clean React project with the complete technical foundation, but don't build the actual application pages yet.

Stack
React
TypeScript
Vite
Tailwind CSS
React Router
Supabase
Zustand
TanStack Query
Axios
React Hook Form
Zod
Lucide React
Sonner
Recharts
Tasks
1. Create project
sciverify/
└── frontend/

Create the React + TypeScript + Vite application.

2. Install dependencies

Set up all required frontend libraries.

3. Configure Tailwind

Create the SciVerify design foundation:

dark background
typography
spacing
border radius
shadows
primary accent
verdict colors
4. Configure environment variables

Create:

.env
.env.example

For example:

VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_BASE_URL=

Never hardcode credentials.

5. Create folder architecture
src/
├── components/
├── pages/
├── layouts/
├── hooks/
├── services/
├── stores/
├── lib/
├── types/
├── routes/
├── constants/
└── assets/
6. Configure aliases

For example:

@/

so imports are clean.

Deliverable

A clean project that runs:

npm run dev

with no errors.

Acceptance criteria
 Vite works
 TypeScript works
 Tailwind works
 Routing works
 Supabase client initialized
 Environment variables work
 ESLint works
 No unnecessary libraries
 Folder structure established