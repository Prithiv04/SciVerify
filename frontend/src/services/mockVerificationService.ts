import {
  VERIFICATION_LOADING_STEPS,
  buildMockVerificationResult,
} from '@/mocks/verification'
import type {
  VerificationFormInput,
  VerificationResult,
} from '@/types/verification'

const MOCK_DELAY_MS = 1800
const STEP_INTERVAL_MS = MOCK_DELAY_MS / VERIFICATION_LOADING_STEPS.length

export async function verifyCitationMock(
  input: VerificationFormInput,
  onProgress?: (step: string) => void,
): Promise<VerificationResult> {
  for (const step of VERIFICATION_LOADING_STEPS) {
    onProgress?.(step)
    await delay(STEP_INTERVAL_MS)
  }

  if (input.claim.toLowerCase().includes('fail')) {
    throw new Error('Mock verification failed. Please try again.')
  }

  return buildMockVerificationResult(input)
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
