import * as authService from '@/services/authService'
import { useAuthStore } from '@/stores/authStore'

export function useAuth() {
  const {
    user,
    session,
    profile,
    initializing,
    isRecoverySession,
  } = useAuthStore()

  return {
    user,
    session,
    profile,
    initializing,
    isRecoverySession,
    loading: initializing,
    isAuthenticated: Boolean(user && session),
    signIn: authService.signIn,
    signUp: authService.signUp,
    signOut: authService.signOut,
    resetPassword: authService.sendPasswordReset,
    updatePassword: authService.updatePassword,
  }
}
