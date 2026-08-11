import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabase'
import { mapAuthError } from '@/lib/auth-errors'
import type { UpdateProfileInput, UserProfile } from '@/types/auth'

export async function getProfile(userId: string): Promise<UserProfile | null> {
  if (!isSupabaseConfigured()) {
    return null
  }

  const { data, error } = await getSupabaseClient()
    .from('profiles')
    .select('*')
    .eq('user_id', userId)
    .maybeSingle()

  if (error) {
    throw new Error(mapAuthError(error, 'Unable to load profile.'))
  }

  return data as UserProfile | null
}

export async function updateProfile(
  userId: string,
  input: UpdateProfileInput,
): Promise<UserProfile> {
  const { data, error } = await getSupabaseClient()
    .from('profiles')
    .update({
      ...input,
      updated_at: new Date().toISOString(),
    })
    .eq('user_id', userId)
    .select('*')
    .single()

  if (error) {
    throw new Error(mapAuthError(error, 'Unable to update profile.'))
  }

  return data as UserProfile
}
