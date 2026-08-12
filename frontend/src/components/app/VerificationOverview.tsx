import { cn } from '@/lib/cn'
import { getVerdictConfig, VERDICT_KEYS } from '@/constants/verdicts'
import type { VerdictKey } from '@/constants/verdicts'
import type { DashboardStats } from '@/types/verification'
import { Divider } from '@/components/ui/Divider'
import { Panel } from '@/components/ui/Card'

export interface VerificationOverviewProps {
  stats: DashboardStats
  className?: string
}

function computeSummary(stats: DashboardStats) {
  return {
    totalRuns: stats.total,
    evidenceAligned: stats.supports,
    needsReview: stats.overstated + stats.insufficient,
    evidenceConflicts: stats.contradicts,
    citationIssues: stats.fabricated,
  }
}

const summaryRows = [
  { key: 'totalRuns', label: 'Total runs' },
  { key: 'evidenceAligned', label: 'Evidence aligned' },
  { key: 'needsReview', label: 'Needs review' },
  { key: 'evidenceConflicts', label: 'Evidence conflicts' },
  { key: 'citationIssues', label: 'Citation issues' },
] as const

export function VerificationOverview({ stats, className }: VerificationOverviewProps) {
  const counts: Record<VerdictKey, number> = {
    SUPPORTS: stats.supports,
    OVERSTATED: stats.overstated,
    CONTRADICTS: stats.contradicts,
    INSUFFICIENT: stats.insufficient,
    FABRICATED: stats.fabricated,
  }

  const maxCount = Math.max(...VERDICT_KEYS.map((key) => counts[key]), 1)
  const summary = computeSummary(stats)

  return (
    <Panel padding="lg" className={cn('flex h-full flex-col', className)}>
      <div>
        <h2 className="text-sm font-semibold text-text-primary">
          Verification overview
        </h2>
        <p className="mt-1 text-xs text-text-muted">
          Distribution of verification outcomes
        </p>
      </div>

      <div className="mt-5 space-y-3.5">
        {VERDICT_KEYS.map((key) => {
          const config = getVerdictConfig(key)
          const count = counts[key]
          const widthPercent =
            count === 0 ? 0 : Math.round((count / maxCount) * 100)

          return (
            <div
              key={key}
              className="grid grid-cols-[5.75rem_minmax(0,1fr)_auto] items-center gap-3 sm:grid-cols-[6.5rem_minmax(0,1fr)_auto]"
            >
              <span className={cn('text-xs font-medium', config.textClass)}>
                {config.label}
              </span>
              <div
                className="h-3 overflow-hidden rounded-sm bg-surface-elevated"
                role="img"
                aria-label={`${config.label}: ${count}`}
              >
                <div
                  className={cn(
                    'h-full rounded-sm transition-all duration-300 motion-reduce:transition-none',
                    config.barClass,
                    count === 0 && 'opacity-0',
                  )}
                  style={{ width: `${Math.max(widthPercent, count > 0 ? 12 : 0)}%` }}
                />
              </div>
              <span className="min-w-[1.25rem] text-right text-xs font-semibold tabular-nums text-text-primary">
                {count}
              </span>
            </div>
          )
        })}
      </div>

      {stats.total === 0 ? (
        <p className="mt-4 text-xs text-text-muted">
          No verification runs yet. Start your first check to populate this overview.
        </p>
      ) : null}

      <div className="mt-auto pt-5">
        <Divider className="mb-4" />
        <h3 className="text-xs font-semibold uppercase tracking-wide text-text-muted">
          Verification summary
        </h3>
        <dl className="mt-3 grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 gap-y-2.5">
          {summaryRows.map((row) => (
            <div key={row.key} className="contents">
              <dt className="text-xs text-text-secondary">{row.label}</dt>
              <dd className="text-right text-xs font-semibold tabular-nums text-text-primary">
                {summary[row.key]}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </Panel>
  )
}
