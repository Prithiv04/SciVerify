import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { cn } from '@/lib/cn'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { verificationReportPath } from '@/constants'
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

function normalize(value: string) {
  return value.trim().toLowerCase()
}

function getSourceLines(record: VerificationResult): string[] {
  const primaryEvidence = record.evidence[0]

  if (primaryEvidence) {
    const lines: string[] = []

    if (primaryEvidence.identifier?.trim()) {
      lines.push(primaryEvidence.identifier.trim())
    }

    if (primaryEvidence.title?.trim()) {
      const title = primaryEvidence.title.trim()
      const isDuplicate = lines.some((line) => normalize(line) === normalize(title))
      if (!isDuplicate) {
        lines.push(title)
      }
    }

    if (lines.length > 0) {
      return lines
    }
  }

  return [record.citation.trim()]
}

export function VerificationActivityCard({
  record,
  className,
}: VerificationActivityCardProps) {
  const sourceLines = getSourceLines(record)

  return (
    <Card
      className={cn(
        'group transition-all duration-200 motion-reduce:transition-none',
        'hover:-translate-y-0.5 hover:border-border/80 hover:shadow-md motion-reduce:hover:translate-y-0',
        className,
      )}
    >
      <CardHeader className="space-y-4 p-5 pb-0">
        <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
          <VerdictBadge verdict={record.verdict} size="sm" />
          <div className="text-right">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">
              Confidence
            </p>
            <p className="text-lg font-semibold tabular-nums leading-none text-text-primary">
              {record.confidence}%
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <p className="break-words text-sm font-medium leading-relaxed text-text-primary">
            {record.claim}
          </p>
          <div className="space-y-1 border-l-2 border-border/80 pl-3">
            {sourceLines.map((line) => (
              <p
                key={`${record.id}-${line}`}
                className={cn(
                  'break-words text-xs leading-relaxed text-text-secondary',
                  record.evidence[0]?.identifier?.trim() === line && 'font-mono',
                )}
              >
                {line}
              </p>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-5 pt-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
          <time
            className="text-xs text-text-muted"
            dateTime={record.createdAt}
          >
            {formatDate(record.createdAt)}
          </time>
          <Link
            to={verificationReportPath(record.id)}
            className="inline-flex items-center gap-1.5 rounded-sm text-sm font-medium text-primary outline-offset-2 transition-colors hover:text-primary-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
          >
            View report
            <ArrowRight className="h-3.5 w-3.5" aria-hidden />
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
