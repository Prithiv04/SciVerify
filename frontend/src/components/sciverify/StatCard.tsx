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
  return (
    <Card className={cn('h-full', className)}>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardDescription>{label}</CardDescription>
            <CardTitle className="mt-2 text-2xl font-semibold tracking-tight">
              {value}
            </CardTitle>
          </div>
          {icon ? (
            <span className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-surface-elevated text-primary">
              {icon}
            </span>
          ) : null}
        </div>
      </CardHeader>
      {(description || trend) && (
        <CardContent className="pt-0">
          {description ? (
            <p className="text-sm text-text-secondary">{description}</p>
          ) : null}
          {trend ? (
            <p className="mt-1 text-xs font-medium text-success">{trend}</p>
          ) : null}
        </CardContent>
      )}
    </Card>
  )
}
