import { Link } from 'react-router-dom'
import {
  AlertTriangle,
  Ban,
  CheckCircle2,
  ClipboardList,
  Plus,
  XCircle,
} from 'lucide-react'
import { AppHeader } from '@/components/app/AppHeader'
import { VerificationOverview } from '@/components/app/VerificationOverview'
import { VerificationWorkflowCta } from '@/components/app/VerificationWorkflowCta'
import { VerificationActivityCard } from '@/components/verification/VerificationActivityCard'
import { computeDashboardStats } from '@/mocks/verification'
import { useVerificationStore } from '@/stores/verificationStore'
import { useUserDisplayName } from '@/hooks/useUserDisplayName'
import { ROUTES } from '@/constants'
import { Button } from '@/components/ui/Button'
import { StatCard } from '@/components/sciverify/StatCard'
import { Panel } from '@/components/ui/Card'

export default function AppHomePage() {
  const displayName = useUserDisplayName()
  const records = useVerificationStore((state) => state.records)
  const stats = computeDashboardStats(records)
  const recentRecords = records.slice(0, 5)

  return (
    <div>
      <AppHeader
        title={`Welcome back, ${displayName}`}
        description="Evidence-backed verification for your scientific claims."
        status={{ label: 'Verification system ready', ready: true }}
        actions={
          <Link to={ROUTES.APP_VERIFY}>
            <Button>
              <Plus className="h-4 w-4" />
              New Verification
            </Button>
          </Link>
        }
      />

      <section aria-label="Verification statistics">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <StatCard
            label="Total Verifications"
            value={stats.total}
            description="All verification runs"
            accent="total"
            icon={<ClipboardList className="h-4 w-4" />}
          />
          <StatCard
            label="Supported"
            value={stats.supports}
            description="Evidence aligned"
            accent="SUPPORTS"
            icon={<CheckCircle2 className="h-4 w-4" />}
          />
          <StatCard
            label="Overstated"
            value={stats.overstated}
            description="Claims requiring review"
            accent="OVERSTATED"
            icon={<AlertTriangle className="h-4 w-4" />}
          />
          <StatCard
            label="Contradicted"
            value={stats.contradicts}
            description="Evidence conflicts"
            accent="CONTRADICTS"
            icon={<XCircle className="h-4 w-4" />}
          />
          <StatCard
            label="Fabricated"
            value={stats.fabricated}
            description="Citation authenticity issue"
            accent="FABRICATED"
            icon={<Ban className="h-4 w-4" />}
          />
        </div>
      </section>

      <section
        className="mt-8 grid gap-4 lg:grid-cols-2"
        aria-label="Verification overview and workflow"
      >
        <VerificationOverview stats={stats} />
        <VerificationWorkflowCta />
      </section>

      <section className="mt-10" aria-label="Recent verification activity">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-text-primary">
            Recent verification activity
          </h2>
          <Link
            to={ROUTES.APP_HISTORY}
            className="text-sm text-primary transition-colors hover:text-primary-hover"
          >
            View all
          </Link>
        </div>

        {recentRecords.length === 0 ? (
          <Panel padding="lg" className="space-y-4 text-center">
            <p className="text-sm text-text-secondary">No verifications yet.</p>
            <Link to={ROUTES.APP_VERIFY} className="inline-block">
              <Button>Start your first verification</Button>
            </Link>
          </Panel>
        ) : (
          <div className="grid gap-4">
            {recentRecords.map((record) => (
              <VerificationActivityCard key={record.id} record={record} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
