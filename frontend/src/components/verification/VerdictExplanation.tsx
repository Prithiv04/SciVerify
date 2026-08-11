import { Check, X } from 'lucide-react'
import { cn } from '@/lib/cn'
import { ConfidenceBar } from '@/components/sciverify/ConfidenceBar'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import { Panel } from '@/components/ui/Card'
import type { VerdictKey } from '@/constants/verdicts'
import type { EvidenceFactor } from '@/types/verification'

export interface VerdictExplanationProps {
  verdict: VerdictKey
  confidence: number
  summary: string
  evidenceFactors: EvidenceFactor[]
  className?: string
}

export function VerdictExplanation({
  verdict,
  confidence,
  summary,
  evidenceFactors,
  className,
}: VerdictExplanationProps) {
  return (
    <Panel padding="md" className={cn('space-y-5', className)}>
      <div className="flex flex-wrap items-center gap-3">
        <VerdictBadge verdict={verdict} size="md" />
        <p className="text-sm text-text-secondary">
          Confidence:{' '}
          <span className="font-semibold text-text-primary">{confidence}%</span>
        </p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
          Short explanation
        </p>
        <p className="mt-2 text-sm leading-relaxed text-text-primary">{summary}</p>
      </div>

      {evidenceFactors.length > 0 ? (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Evidence factors
          </p>
          <ul className="mt-3 space-y-2">
            {evidenceFactors.map((factor) => (
              <li
                key={factor.text}
                className="flex items-start gap-2 text-sm text-text-secondary"
              >
                {factor.supported ? (
                  <Check
                    className="mt-0.5 h-4 w-4 shrink-0 text-success"
                    aria-label="Supported"
                  />
                ) : (
                  <X
                    className="mt-0.5 h-4 w-4 shrink-0 text-danger"
                    aria-label="Not supported"
                  />
                )}
                <span>{factor.text}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <ConfidenceBar value={confidence} verdict={verdict} label="Confidence" />
    </Panel>
  )
}
