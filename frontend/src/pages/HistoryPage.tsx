import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { AppHeader } from '@/components/app/AppHeader'
import { useVerificationStore } from '@/stores/verificationStore'
import { ROUTES } from '@/constants'
import { getVerdictConfig, VERDICT_KEYS } from '@/constants/verdicts'
import type { VerdictKey } from '@/constants/verdicts'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import { ConfidenceBar } from '@/components/sciverify/ConfidenceBar'
import { Panel } from '@/components/ui/Card'

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
  }).format(new Date(value))
}

export default function HistoryPage() {
  const records = useVerificationStore((state) => state.records)
  const [search, setSearch] = useState('')
  const [verdictFilter, setVerdictFilter] = useState<'all' | VerdictKey>('all')

  const filteredRecords = useMemo(() => {
    return records.filter((record) => {
      const matchesSearch =
        search.trim().length === 0 ||
        record.claim.toLowerCase().includes(search.toLowerCase()) ||
        record.citation.toLowerCase().includes(search.toLowerCase())

      const matchesVerdict =
        verdictFilter === 'all' || record.verdict === verdictFilter

      return matchesSearch && matchesVerdict
    })
  }, [records, search, verdictFilter])

  return (
    <div>
      <AppHeader
        title="Verification History"
        description="Review previous mock verification runs and reopen their results."
      />

      <div className="mb-6 grid gap-4 md:grid-cols-[1fr_220px]">
        <Input
          label="Search"
          placeholder="Search claims or citations..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <Select
          label="Verdict filter"
          value={verdictFilter}
          onChange={(event) =>
            setVerdictFilter(event.target.value as 'all' | VerdictKey)
          }
          options={[
            { value: 'all', label: 'All verdicts' },
            ...VERDICT_KEYS.map((key) => ({
              value: key,
              label: getVerdictConfig(key).label,
            })),
          ]}
        />
      </div>

      {filteredRecords.length === 0 ? (
        <Panel padding="lg" className="text-center">
          <p className="text-sm text-text-secondary">
            {records.length === 0
              ? 'No verification history yet.'
              : 'No records match your search or filter.'}
          </p>
        </Panel>
      ) : (
        <div className="space-y-4">
          {filteredRecords.map((record) => (
            <Panel key={record.id} padding="md" className="space-y-4">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="min-w-0 space-y-2">
                  <p className="line-clamp-2 font-medium text-text-primary">
                    {record.claim}
                  </p>
                  <p className="line-clamp-1 text-sm text-text-secondary">
                    {record.citation}
                  </p>
                  <div className="flex flex-wrap items-center gap-2">
                    <VerdictBadge verdict={record.verdict} size="sm" />
                    <span className="text-xs text-text-muted">
                      {formatDate(record.createdAt)}
                    </span>
                  </div>
                </div>
                <Link
                  to={ROUTES.APP_VERIFY}
                  state={{ recordId: record.id }}
                  className="shrink-0"
                >
                  <Button variant="outline" size="sm">
                    View
                  </Button>
                </Link>
              </div>
              <ConfidenceBar
                value={record.confidence}
                verdict={record.verdict}
                size="sm"
              />
            </Panel>
          ))}
        </div>
      )}
    </div>
  )
}
