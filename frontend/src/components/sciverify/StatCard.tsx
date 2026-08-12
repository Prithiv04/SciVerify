import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

export interface StatCardProps {
  label: string
  value: string | number
  description?: string
  trend?: string
  icon?: ReactNode
  className?: string
}

export function StatCard({
  label,
  value,
  description,
  trend,
  icon,
  className,
}: StatCardProps) {
  const hasFooter = Boolean(description || trend)

  return (
    <Card
      className={cn(
        'flex h-full min-h-[8.5rem] flex-col transition-all duration-200 motion-reduce:transition-none',
        'hover:-translate-y-0.5 hover:border-border/80 hover:shadow-md motion-reduce:hover:translate-y-0',
        className,
      )}
    >
      <CardHeader
        className={cn(
          'flex flex-1 flex-col gap-0 p-5',
          hasFooter ? 'pb-0' : 'pb-5',
        )}
      >
        <div className="flex items-start justify-between gap-3">
          <CardDescription className="min-h-[2.75rem] flex-1 text-xs font-semibold uppercase tracking-wide text-text-muted">
            {label}
          </CardDescription>
          {icon ? (
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border/80 bg-surface-elevated text-primary">
              {icon}
            </span>
          ) : null}
        </div>
        <CardTitle className="mt-4 text-3xl font-semibold tabular-nums leading-none tracking-tight text-text-primary">
          {value}
        </CardTitle>
      </CardHeader>
      {hasFooter ? (
        <CardContent className="mt-auto pt-3">
          {description ? (
            <p className="text-xs leading-relaxed text-text-muted">{description}</p>
          ) : null}
          {trend ? (
            <p className="mt-1 text-xs font-medium text-success">{trend}</p>
          ) : null}
        </CardContent>
      ) : null}
    </Card>
  )
}
