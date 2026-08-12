import { cn } from '@/lib/cn'
import { StatCard } from '@/components/sciverify/StatCard'
import { Panel } from '@/components/ui/Card'
import { computeAverageConfidence } from '@/lib/dashboard-selectors'
import type { DashboardStats } from '@/types/verification'
import type { VerificationResult } from '@/types/verification'
import { Gauge } from 'lucide-react'

export interface WorkspaceInsightsProps {
  records: VerificationResult[]
  stats: DashboardStats
  className?: string
}

export function WorkspaceInsights({
  records,
  stats,
  className,
}: WorkspaceInsightsProps) {
  const averageConfidence = computeAverageConfidence(records)

  return (
    <Panel padding="lg" className={cn('flex h-full flex-col', className)}>
      <h2 className="text-sm font-semibold text-text-primary">Workspace insights</h2>
      <p className="mt-1 text-xs text-text-muted">
        Demo verification environment — mock data only
      </p>

      <div className="mt-5 flex flex-1 flex-col gap-4">
        <div className="rounded-lg border border-border/70 bg-surface/60 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">
            Verification health
          </p>
          <p className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-text-primary">
            <span className="h-2 w-2 rounded-full bg-success" aria-hidden />
            System ready
          </p>
          <p className="mt-2 text-xs leading-relaxed text-text-secondary">
            {stats.total} verification {stats.total === 1 ? 'run' : 'runs'} in
            this demo workspace. Results are simulated and do not reflect live
            scientific verification.
          </p>
        </div>

        <StatCard
          label="Average confidence"
          value={
            averageConfidence !== null ? `${averageConfidence}%` : '—'
          }
          description={
            stats.total > 0
              ? `Across ${stats.total} verification${stats.total === 1 ? '' : 's'}`
              : 'No verifications yet'
          }
          icon={<Gauge className="h-4 w-4" />}
          accent="total"
          className="mt-auto"
        />
      </div>
    </Panel>
  )
}
