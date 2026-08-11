export default function FoundationPlaceholder() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3">
      <h1 className="text-2xl font-semibold text-text-primary">SciVerify</h1>
      <p className="text-text-secondary">Foundation ready.</p>
      <a
        href="/ui-preview"
        className="mt-2 text-sm text-primary hover:text-primary-hover"
      >
        Open UI preview
      </a>
    </div>
  )
}
