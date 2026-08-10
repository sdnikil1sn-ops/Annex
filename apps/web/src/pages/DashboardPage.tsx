import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { createAnalysis, listAnalyses, uploadMedia, type Analysis } from '../api'
import Skeleton from '../components/Skeleton'

type Tab = 'text' | 'image' | 'audio' | 'video'

const TABS: { value: Tab; label: string }[] = [
  { value: 'text', label: 'Text' },
  { value: 'image', label: 'Image' },
  { value: 'audio', label: 'Audio' },
  { value: 'video', label: 'Video' },
]

function StatusBadge({ status }: { status: Analysis['status'] }) {
  const styles: Record<Analysis['status'], string> = {
    pending: 'bg-amber-100 text-amber-800',
    processing: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  }
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${styles[status] ?? 'bg-slate-100 text-slate-700'}`}>
      {status}
    </span>
  )
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [tab, setTab] = useState<Tab>('text')
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState('')

  const {
    data: analyses,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['analyses'],
    queryFn: listAnalyses,
  })

  const mutation = useMutation({
    mutationFn: async () => {
      if (tab === 'text') {
        if (!text.trim()) throw new Error('Enter some text to analyze.')
        return createAnalysis({
          type: 'text',
          title: title.trim() || undefined,
          input_payload: { text },
        })
      }
      if (!file) throw new Error('Choose a file to upload.')
      const media = await uploadMedia(file)
      return createAnalysis({
        type: tab,
        title: title.trim() || undefined,
        input_payload: {
          path: media.path,
          url: media.url,
          content_type: file.type,
        },
      })
    },
    onSuccess: (analysis) => {
      queryClient.invalidateQueries({ queryKey: ['analyses'] })
      navigate(`/analyses/${analysis.id}`)
    },
    onError: (err) => setError((err as Error).message),
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setError('')
    mutation.mutate()
  }

  const canSubmit = mutation.isPending || (tab === 'text' ? !text.trim() : !file)

  return (
    <div className="space-y-10">
      <section>
        <h2 className="mb-3 text-xl font-semibold text-slate-900">New analysis</h2>
        <div className="mb-4 flex gap-2">
          {TABS.map((t) => (
            <button
              key={t.value}
              type="button"
              onClick={() => setTab(t.value)}
              className={`rounded-lg px-4 py-1.5 text-sm font-medium ${
                tab === t.value
                  ? 'bg-slate-900 text-white'
                  : 'bg-white text-slate-600 ring-1 ring-slate-300 hover:bg-slate-100'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 rounded-xl border bg-white p-5 shadow-sm">
          <input
            type="text"
            placeholder="Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />

          {tab === 'text' ? (
            <textarea
              placeholder="Paste a claim, headline, or passage to fact-check…"
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          ) : (
            <input
              type="file"
              accept={tab === 'image' ? 'image/*' : undefined}
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200"
            />
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={canSubmit}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {mutation.isPending ? 'Analyzing…' : 'Analyze'}
          </button>
        </form>
      </section>

      <section>
        <h2 className="mb-3 text-xl font-semibold text-slate-900">Recent analyses</h2>

        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-14 w-full" />
            <Skeleton className="h-14 w-full" />
            <Skeleton className="h-14 w-full" />
          </div>
        ) : isError ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            <p>Could not load your analyses.</p>
            <button
              type="button"
              onClick={() => refetch()}
              className="mt-2 rounded-md border border-red-300 px-3 py-1 hover:bg-red-100"
            >
              Retry
            </button>
          </div>
        ) : analyses && analyses.length > 0 ? (
          <ul className="divide-y rounded-xl border bg-white shadow-sm">
            {analyses.map((a) => (
              <li key={a.id}>
                <Link
                  to={`/analyses/${a.id}`}
                  className="flex items-center justify-between gap-4 px-5 py-3 hover:bg-slate-50"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-900">
                      {a.title || a.type}
                    </p>
                    <p className="truncate text-xs text-slate-500">
                      {a.summary ?? new Date(a.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    {a.credibility_score != null && (
                      <span className="text-sm font-semibold text-slate-700">
                        {a.credibility_score}/100
                      </span>
                    )}
                    <StatusBadge status={a.status} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">No analyses yet — create your first one above.</p>
        )}
      </section>
    </div>
  )
}
