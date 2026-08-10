import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { getAnalysis, type Claim } from '../api'
import Skeleton from '../components/Skeleton'

const STATUS_LABEL: Record<string, string> = {
  pending: 'Queued…',
  processing: 'Analyzing…',
  completed: 'Completed',
  failed: 'Failed',
}

function VerdictBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    verified: 'bg-green-100 text-green-800',
    partially_verified: 'bg-amber-100 text-amber-800',
    disputed: 'bg-orange-100 text-orange-800',
    debunked: 'bg-red-100 text-red-800',
  }
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${styles[status] ?? 'bg-slate-100 text-slate-700'}`}>
      {status.replace('_', ' ')}
    </span>
  )
}

function ClaimCard({ claim }: { claim: Claim }) {
  return (
    <li className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm font-medium text-slate-900">{claim.claim_text}</p>
        <VerdictBadge status={claim.status} />
      </div>

      <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
        <span>Confidence: {claim.confidence}/100</span>
      </div>

      {claim.sources && claim.sources.length > 0 && (
        <div className="mt-4">
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">Sources</p>
          <ul className="space-y-1">
            {claim.sources.map((s) => (
              <li key={s.id}>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  {s.title || s.url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {claim.evidence && claim.evidence.length > 0 && (
        <div className="mt-4">
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">Evidence</p>
          <ul className="space-y-2">
            {claim.evidence.map((e) => (
              <li key={e.id} className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
                “{e.quote}”
                {e.url && (
                  <a href={e.url} target="_blank" rel="noreferrer" className="ml-1 text-blue-600 hover:underline">
                    source
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </li>
  )
}

export default function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: analysis, isLoading, isError } = useQuery({
    queryKey: ['analysis', id],
    queryFn: () => getAnalysis(id!),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'pending' || status === 'processing' ? 2000 : false
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (isError || !analysis) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-red-600">Could not load this analysis.</p>
        <Link to="/" className="text-sm text-blue-600 hover:underline">← Back to dashboard</Link>
      </div>
    )
  }

  const polling = analysis.status === 'pending' || analysis.status === 'processing'

  return (
    <div className="space-y-6">
      <div>
        <Link to="/" className="text-sm text-blue-600 hover:underline">← Back to dashboard</Link>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <h2 className="text-2xl font-semibold text-slate-900">
            {analysis.title || analysis.type}
          </h2>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
            {analysis.type}
          </span>
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
            {polling ? STATUS_LABEL[analysis.status] : analysis.status}
          </span>
        </div>
        <p className="mt-1 text-xs text-slate-500">
          {new Date(analysis.created_at).toLocaleString()}
        </p>
      </div>

      {polling && (
        <p className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
          This analysis is running — refreshing automatically…
        </p>
      )}

      {analysis.credibility_score != null && (
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Credibility score</p>
          <p className="mt-1 text-3xl font-semibold text-slate-900">
            {analysis.credibility_score}
            <span className="text-base font-normal text-slate-500">/100</span>
          </p>
        </div>
      )}

      {analysis.summary && (
        <p className="rounded-xl border bg-white p-4 text-sm text-slate-700 shadow-sm">
          {analysis.summary}
        </p>
      )}

      {analysis.status === 'failed' && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          This analysis failed. Check the backend logs for details.
        </p>
      )}

      {analysis.claims && analysis.claims.length > 0 ? (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-slate-900">
            Claims ({analysis.claims.length})
          </h3>
          <ul className="space-y-4">
            {analysis.claims.map((claim) => (
              <ClaimCard key={claim.id} claim={claim} />
            ))}
          </ul>
        </section>
      ) : (
        !polling && (
          <p className="text-sm text-slate-500">No claims found.</p>
        )
      )}
    </div>
  )
}
