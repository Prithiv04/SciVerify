import { VerificationReportView } from '@/components/verification/VerificationReportView'
import type { VerificationResult } from '@/types/verification'

export interface VerificationResultViewProps {
  result: VerificationResult
}

export function VerificationResultView({ result }: VerificationResultViewProps) {
  return <VerificationReportView result={result} />
}
