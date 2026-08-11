import { Link } from 'react-router-dom'
import { ROUTES } from '@/constants'

export default function FoundationPlaceholder() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3">
      <h1 className="text-2xl font-semibold text-text-primary">SciVerify</h1>
      <p className="text-text-secondary">Foundation ready.</p>
      <div className="mt-2 flex flex-wrap items-center justify-center gap-4 text-sm">
        <Link to={ROUTES.UI_PREVIEW} className="text-primary hover:text-primary-hover">
          Open UI preview
        </Link>
        <Link to={ROUTES.LOGIN} className="text-primary hover:text-primary-hover">
          Sign in
        </Link>
      </div>
    </div>
  )
}
