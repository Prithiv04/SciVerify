import { Link } from 'react-router-dom'
import { ArrowRight, Plus } from 'lucide-react'
import { AppHeader } from '@/components/app/AppHeader'
import { computeDashboardStats } from '@/mocks/verification'
import { useVerificationStore } from '@/stores/verificationStore'
import { useUserDisplayName } from '@/hooks/useUserDisplayName'
import { ROUTES } from '@/constants'
import { Button } from '@/components/ui/Button'
import { StatCard } from '@/components/sciverify/StatCard'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import { ConfidenceBar } from '@/components/sciverify/ConfidenceBar'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card'
import { Panel } from '@/components/ui/Card'

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export default function AppHomePage() {
  const displayName = useUserDisplayName()
  const records = useVerificationStore((state) => state.records)
  const stats = computeDashboardStats(records)
  const recentRecords = records.slice(0, 5)

  return (
    <div>
      <AppHeader
        title={`Welcome back, ${displayName}`}
        description="Verify scientific claims against their cited evidence."
        actions={
          <Link to={ROUTES.APP_VERIFY}>
            <Button>
              <Plus className="h-4 w-4" />
              New Verification
            </Button>
          </Link>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Total Verifications" value={stats.total} />
        <StatCard label="Supported" value={stats.supports} />
        <StatCard label="Overstated" value={stats.overstated} />
        <StatCard label="Contradicted" value={stats.contradicts} />
        <StatCard
          label="Unclear"
          value={stats.insufficient + stats.fabricated}
          description="Insufficient or fabricated"
        />
      </div>

      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-text-primary">
            Recent Verifications
          </h2>
          <Link
            to={ROUTES.APP_HISTORY}
            className="text-sm text-primary hover:text-primary-hover"
          >
            View all
          </Link>
        </div>

        {recentRecords.length === 0 ? (
          <Panel padding="lg" className="text-center">
            <p className="text-sm text-text-secondary">
              No verification records yet. Start your first citation check.
            </p>
            <Link to={ROUTES.APP_VERIFY} className="mt-4 inline-block">
              <Button>New Verification</Button>
            </Link>
          </Panel>
        ) : (
          <div className="grid gap-4">
            {recentRecords.map((record) => (
              <Card key={record.id}>
                <CardHeader>
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0 space-y-2">
                      <CardTitle className="line-clamp-2 text-base">
                        {record.claim}
                      </CardTitle>
                      <CardDescription className="line-clamp-1">
                        {record.citation}
                      </CardDescription>
                      <div className="flex flex-wrap items-center gap-2">
                        <VerdictBadge verdict={record.verdict} size="sm" />
                        <span className="text-xs text-text-muted">
                          {formatDate(record.createdAt)}
                        </span>
                      </div>
                    </div>
                    <Link to={ROUTES.APP_VERIFY} state={{ recordId: record.id }}>
                      <Button variant="outline" size="sm">
                        View
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <ConfidenceBar
                    value={record.confidence}
                    verdict={record.verdict}
                    size="sm"
                  />
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
