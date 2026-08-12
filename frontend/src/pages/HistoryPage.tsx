import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Filter, Search } from 'lucide-react'
import { AppHeader } from '@/components/app/AppHeader'
import { VerificationActivityCard } from '@/components/verification/VerificationActivityCard'
import { useVerificationStore } from '@/stores/verificationStore'
import { ROUTES } from '@/constants'
import { getVerdictConfig, VERDICT_KEYS } from '@/constants/verdicts'
import type { VerdictKey } from '@/constants/verdicts'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Panel } from '@/components/ui/Card'

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
        title="Verification history"
        description="Review previous verification runs and reopen complete reports."
      />

      <Panel padding="md" className="mb-6">
        <div className="grid gap-4 md:grid-cols-[1fr_220px]">
            <Input
              label="Search"
              placeholder="Search claims or citations..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              leftIcon={<Search className="h-4 w-4" />}
            />
          <div>
            <div className="mb-1.5 flex items-center gap-1.5 text-sm font-medium text-text-primary">
              <Filter className="h-4 w-4 text-text-muted" />
              Verdict filter
            </div>
            <Select
              aria-label="Verdict filter"
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
        </div>
      </Panel>

      {filteredRecords.length === 0 ? (
        <Panel padding="lg" className="space-y-4 text-center">
          <p className="text-sm text-text-secondary">
            {records.length === 0
              ? 'No verifications yet.'
              : 'No records match your search or filter.'}
          </p>
          {records.length === 0 ? (
            <Link to={ROUTES.APP_VERIFY}>
              <Button>Start your first verification</Button>
            </Link>
          ) : null}
        </Panel>
      ) : (
        <div className="grid gap-4">
          {filteredRecords.map((record) => (
            <VerificationActivityCard key={record.id} record={record} />
          ))}
        </div>
      )}
    </div>
  )
}
