import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { Panel } from '@/components/ui/Card'
import { computeAverageConfidence } from '@/lib/dashboard-selectors'
import type { DashboardStats } from '@/types/verification'
import type { VerificationResult } from '@/types/verification'

export interface WorkspaceInsightsProps {
  records: VerificationResult[]
  stats: DashboardStats
  className?: string
}

function MetricBlock({
  value,
  label,
  valueClassName,
  children,
}: {
  value: ReactNode
  label: string
  valueClassName?: string
  children?: ReactNode
}) {
  return (
    <div className="rounded-lg border border-border/70 bg-surface/60 px-3 py-3">
      <div className={cn('text-lg font-semibold tabular-nums leading-none text-text-primary', valueClassName)}>
        {children ?? value}
      </div>
      <p className="mt-1.5 text-[11px] font-medium uppercase tracking-wide text-text-muted">
        {label}
      </p>
    </div>
  )
}

export function WorkspaceInsights({
  records,
  stats,
  className,
}: WorkspaceInsightsProps) {
  const averageConfidence = computeAverageConfidence(records)

  return (
    <Panel padding="md" className={cn(className)}>
      <h2 className="text-sm font-semibold text-text-primary">Workspace insights</h2>
      <p className="mt-1 text-xs text-text-muted">Demo verification environment</p>

      <div className="mt-4 grid grid-cols-1 gap-2.5 sm:grid-cols-3">
        <MetricBlock
          value="System ready"
          label="Verification health"
          valueClassName="text-sm font-medium"
        >
          <span className="inline-flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-success" aria-hidden />
            System ready
          </span>
        </MetricBlock>

        <MetricBlock
          value={stats.total}
          label="Verifications"
          valueClassName="text-2xl"
        />

        <MetricBlock
          value={averageConfidence !== null ? `${averageConfidence}%` : '—'}
          label="Avg confidence"
          valueClassName="text-2xl"
        />
      </div>

      <p className="mt-3 text-[11px] leading-relaxed text-text-muted">
        Results are simulated demo data and do not reflect live scientific
        verification.
      </p>
    </Panel>
  )
}
