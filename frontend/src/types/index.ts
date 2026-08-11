export type {
  UserProfile,
  AuthState,
  LoginFormData,
  RegisterFormData,
  ForgotPasswordFormData,
  ResetPasswordFormData,
  SignUpResult,
  UpdateProfileInput,
} from '@/types/auth'

export type { VerdictKey } from '@/constants/verdicts'

export type AgentStatus = 'idle' | 'running' | 'completed' | 'error'

export type TimelineStepStatus = 'pending' | 'active' | 'completed' | 'error'

export interface ApiError {
  message: string
  status?: number
}
