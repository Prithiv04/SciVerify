export { VERDICTS, VERDICT_KEYS, getVerdictConfig } from '@/constants/verdicts'
export type { VerdictKey, VerdictConfig } from '@/constants/verdicts'

export const ROUTES = {
  HOME: '/',
  UI_PREVIEW: 'ui-preview',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  APP: '/app',
  APP_HOME: '/app/home',
} as const
