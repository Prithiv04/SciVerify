export const ROUTES = {
  HOME: '/',
} as const

export const VERDICT_LABELS = {
  true: 'Supported',
  false: 'Refuted',
  mixed: 'Mixed',
  unverified: 'Unverified',
} as const

export const VERDICT_COLORS = {
  true: 'text-verdict-true',
  false: 'text-verdict-false',
  mixed: 'text-verdict-mixed',
  unverified: 'text-verdict-unverified',
} as const
