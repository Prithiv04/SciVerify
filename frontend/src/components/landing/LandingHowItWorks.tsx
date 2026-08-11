import { Reveal } from '@/components/landing/Reveal'

const steps = [
  {
    step: '01',
    title: 'Submit a claim or citation',
    description:
      'Provide a DOI, citation string, or excerpted claim from a manuscript or review.',
  },
  {
    step: '02',
    title: 'Agents retrieve and analyze evidence',
    description:
      'Specialized agents parse metadata, query literature, and cross-check source alignment.',
  },
  {
    step: '03',
    title: 'Receive a structured verdict',
    description:
      'SciVerify returns a verdict type, confidence score, and evidence cards you can inspect.',
  },
]

export function LandingHowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-20 px-4 py-20 sm:px-6 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <Reveal>
          <p className="text-sm font-medium uppercase tracking-wider text-primary">
            Workflow
          </p>
          <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight text-text-primary sm:text-4xl">
            How SciVerify works
          </h2>
          <p className="mt-4 max-w-2xl text-text-secondary">
            A focused verification pipeline designed for research workflows — not
            open-ended chat.
          </p>
        </Reveal>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {steps.map((item, index) => (
            <Reveal key={item.step} delay={index * 120}>
              <div className="group relative h-full rounded-xl border border-border bg-surface p-6 transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 hover:shadow-lg">
                <span className="text-xs font-mono font-medium text-primary">
                  {item.step}
                </span>
                <h3 className="mt-4 text-lg font-semibold text-text-primary">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                  {item.description}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
