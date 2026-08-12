import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/cn'
import { countNeedsReview } from '@/lib/dashboard-selectors'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import { ROUTES, verificationReportPath } from '@/constants'
import { Panel } from '@/components/ui/Card'
import type { VerificationResult } from '@/types/verification'

export interface NeedsReviewSectionProps {
  records: VerificationResult[]
  needsReviewRecords: VerificationResult[]
  className?: string
}

export function NeedsReviewSection({
  records,
  needsReviewRecords,
  className,
}: NeedsReviewSectionProps) {
  const attentionCount = countNeedsReview(records)

  return (
    <Panel padding="lg" className={cn('flex h-full flex-col', className)}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-text-primary">Needs review</h2>
          <p className="mt-1 text-xs text-text-muted">
            {attentionCount > 0
              ? `${attentionCount} ${attentionCount === 1 ? 'claim requires' : 'claims require'} attention`
              : 'No claims require attention'}
          </p>
        </div>
        {attentionCount > 0 ? (
          <Link
            to={ROUTES.APP_HISTORY}
            className="inline-flex shrink-0 items-center gap-1 text-xs font-medium text-primary hover:text-primary-hover"
          >
            View all
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        ) : null}
      </div>

      {needsReviewRecords.length === 0 ? (
        <div className="mt-6 flex flex-1 flex-col items-center justify-center gap-3 py-8 text-center">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-surface-elevated">
            <CheckCircle2 className="h-4 w-4 text-success" />
          </span>
          <div className="space-y-1">
            <p className="text-sm font-medium text-text-primary">
              No claims require attention
            </p>
            <p className="mx-auto max-w-xs text-sm text-text-secondary">
              All recent verification results are evidence-aligned.
            </p>
          </div>
        </div>
      ) : (
        <ul className="mt-5 flex flex-1 flex-col gap-3">
          {needsReviewRecords.map((record) => (
            <li
              key={record.id}
              className="rounded-lg border border-border/70 bg-surface/60 p-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
                <VerdictBadge verdict={record.verdict} size="sm" />
                <span className="text-sm font-semibold tabular-nums text-text-primary">
                  {record.confidence}%
                </span>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-text-primary">
                {record.claim}
              </p>
              <div className="mt-4 flex justify-end border-t border-border/60 pt-3">
                <Link
                  to={verificationReportPath(record.id)}
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary-hover"
                >
                  View report
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  )
}
