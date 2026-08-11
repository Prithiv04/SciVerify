import { createClient } from '@supabase/supabase-js'
import { env } from '@/lib/env'

if (!env.supabaseUrl || !env.supabaseAnonKey) {
  console.warn(
    'Supabase environment variables are missing. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.',
  )
}

export const supabase = createClient(env.supabaseUrl, env.supabaseAnonKey)
