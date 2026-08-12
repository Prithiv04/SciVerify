import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { cn } from '@/lib/cn'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import { ConfidenceBar } from '@/components/sciverify/ConfidenceBar'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { ROUTES } from '@/constants'
import type { VerificationResult } from '@/types/verification'

export interface VerificationActivityCardProps {
  record: VerificationResult
  className?: string
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
  }).format(new Date(value))
}

export function VerificationActivityCard({
  record,
  className,
}: VerificationActivityCardProps) {
  return (
    <Card
      className={cn(
        'group transition-all duration-200 motion-reduce:transition-none',
        'hover:-translate-y-0.5 hover:border-border/80 hover:shadow-md motion-reduce:hover:translate-y-0',
        className,
      )}
    >
      <CardHeader className="space-y-4 p-5 pb-0">
        <div className="flex items-start justify-between gap-4">
          <VerdictBadge verdict={record.verdict} size="sm" />
          <span className="text-sm font-semibold tabular-nums text-text-primary">
            {record.confidence}%
          </span>
        </div>

        <div className="space-y-2">
          <p className="line-clamp-2 text-sm font-medium leading-relaxed text-text-primary">
            {record.claim}
          </p>
          <p className="line-clamp-1 font-mono text-xs text-text-muted">
            {record.citation}
          </p>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 p-5 pt-4">
        <ConfidenceBar
          value={record.confidence}
          verdict={record.verdict}
          size="sm"
          label="Confidence"
        />

        <div className="flex items-center justify-between gap-3 border-t border-border pt-4">
          <span className="text-xs text-text-muted">
            {formatDate(record.createdAt)}
          </span>
          <Link
            to={ROUTES.APP_VERIFY}
            state={{ recordId: record.id }}
            className="inline-flex items-center gap-1.5 text-sm font-medium text-primary transition-transform duration-200 group-hover:translate-x-0.5 motion-reduce:transform-none"
          >
            View report
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
