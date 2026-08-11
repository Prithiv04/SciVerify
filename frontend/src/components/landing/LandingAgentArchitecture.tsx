import { Reveal } from '@/components/landing/Reveal'
import { AgentCard } from '@/components/sciverify/AgentCard'

const agents = [
  {
    name: 'Citation Parser',
    role: 'Structured extraction',
    status: 'completed' as const,
    description:
      'Extracts claim spans, bibliographic metadata, and reference identifiers from submitted text or PDFs.',
  },
  {
    name: 'Evidence Retriever',
    role: 'Literature discovery',
    status: 'running' as const,
    description:
      'Queries scientific indexes and retrieves candidate sources aligned with the parsed claim context.',
  },
  {
    name: 'Verdict Synthesizer',
    role: 'Evidence aggregation',
    status: 'idle' as const,
    description:
      'Combines agent outputs into a final verdict, confidence score, and inspectable evidence trail.',
  },
]

export function LandingAgentArchitecture() {
  return (
    <section id="agents" className="scroll-mt-20 px-4 py-20 sm:px-6 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <Reveal>
          <p className="text-sm font-medium uppercase tracking-wider text-primary">
            Architecture
          </p>
          <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight text-text-primary sm:text-4xl">
            Three-agent verification system
          </h2>
          <p className="mt-4 max-w-2xl text-text-secondary">
            Each agent has a narrow responsibility — improving reliability,
            auditability, and research fit.
          </p>
        </Reveal>

        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {agents.map((agent, index) => (
            <Reveal key={agent.name} delay={index * 120}>
              <AgentCard {...agent} className="h-full" />
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
