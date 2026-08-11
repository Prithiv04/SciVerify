import { useNavigate } from 'react-router-dom'
import { LogOut, ShieldCheck, UserRound } from 'lucide-react'
import { toast } from 'sonner'
import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { ROUTES } from '@/constants'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card'
import { Divider } from '@/components/ui/Divider'

export default function AuthHomePage() {
  const navigate = useNavigate()
  const { user, profile, signOut } = useAuth()
  const [signingOut, setSigningOut] = useState(false)

  const displayName =
    profile?.full_name ??
    (typeof user?.user_metadata?.full_name === 'string'
      ? user.user_metadata.full_name
      : null)

  const handleSignOut = async () => {
    try {
      setSigningOut(true)
      await signOut()
      toast.success('Signed out successfully.')
      navigate(ROUTES.HOME, { replace: true })
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : 'Unable to sign out.',
      )
    } finally {
      setSigningOut(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-2xl flex-col justify-center py-8">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <span className="flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-surface-elevated">
                <ShieldCheck className="h-6 w-6 text-primary" />
              </span>
              <div>
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <CardTitle>Welcome to SciVerify</CardTitle>
                  <Badge variant="success">Authenticated</Badge>
                </div>
                <CardDescription>
                  Authentication successful. This temporary workspace will be
                  replaced by the real dashboard in a later phase.
                </CardDescription>
              </div>
            </div>
            <Button
              variant="outline"
              onClick={handleSignOut}
              loading={signingOut}
            >
              <LogOut className="h-4 w-4" />
              {signingOut ? 'Signing out...' : 'Logout'}
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-5">
          <Divider label="Account" />

          <div className="flex items-center gap-4 rounded-xl border border-border bg-surface-elevated/60 p-4">
            <Avatar
              name={displayName ?? user?.email ?? 'User'}
              size="lg"
            />
            <div className="min-w-0 space-y-1">
              <div className="flex items-center gap-2">
                <UserRound className="h-4 w-4 text-text-muted" />
                <p className="truncate font-medium text-text-primary">
                  {displayName ?? 'SciVerify User'}
                </p>
              </div>
              <p className="truncate text-sm text-text-secondary">
                {user?.email}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
