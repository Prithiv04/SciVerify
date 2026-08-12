import { Link } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowRight,
  Ban,
  CheckCircle2,
  ClipboardList,
  Plus,
  XCircle,
} from 'lucide-react'
import { AppHeader } from '@/components/app/AppHeader'
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
            icon={<ClipboardList className="h-4 w-4" />}
          />
          <StatCard
            label="Supported"
            value={stats.supports}
            description="Evidence aligned"
            icon={<CheckCircle2 className="h-4 w-4" />}
          />
          <StatCard
            label="Overstated"
            value={stats.overstated}
            description="Claims requiring review"
            icon={<AlertTriangle className="h-4 w-4" />}
          />
          <StatCard
            label="Contradicted"
            value={stats.contradicts}
            description="Evidence conflicts"
            icon={<XCircle className="h-4 w-4" />}
          />
          <StatCard
            label="Fabricated"
            value={stats.fabricated}
            description="Citation authenticity issue"
            icon={<Ban className="h-4 w-4" />}
          />
        </div>
      </section>

      <Panel
        padding="lg"
        className="mt-8 border-primary/15 bg-gradient-to-br from-primary/5 via-surface-elevated/40 to-surface"
      >
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl space-y-2">
            <h2 className="text-lg font-semibold text-text-primary">
              Verify a scientific claim
            </h2>
            <p className="text-sm leading-relaxed text-text-secondary">
              Compare the claim against its cited evidence using Prosecutor,
              Defender, and Adjudicator.
            </p>
          </div>
          <Link to={ROUTES.APP_VERIFY} className="shrink-0">
            <Button>
              Start verification
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </Panel>

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
