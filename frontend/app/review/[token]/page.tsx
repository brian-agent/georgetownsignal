'use client'
import { useEffect, useState } from 'react'
import { Star, CheckCircle, Clock } from 'lucide-react'

interface Props { params: { token: string } }

type Step = 'loading' | 'form' | 'submitted' | 'error'

export default function QuestionnairePage({ params }: Props) {
  const [step,        setStep]        = useState<Step>('loading')
  const [bizName,     setBizName]     = useState('')
  const [category,    setCategory]    = useState('')
  const [errorMsg,    setErrorMsg]    = useState('')
  const [submitting,  setSubmitting]  = useState(false)

  const [form, setForm] = useState({
    response_time_minutes: '',
    job_completed:         '',
    would_recommend:       '',
    review_text:           '',
    rating:                0,
  })

  const API = process.env.NEXT_PUBLIC_API_URL

  useEffect(() => {
    fetch(`${API}/api/reviews/questionnaire/${params.token}/`)
      .then(async r => {
        if (!r.ok) {
          const d = await r.json()
          setErrorMsg(d.error ?? 'This link is invalid or has expired.')
          setStep('error')
          return
        }
        const d = await r.json()
        setBizName(d.business_name)
        setCategory(d.category)
        setStep('form')
      })
      .catch(() => { setErrorMsg('Could not load the review form.'); setStep('error') })
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    const payload = {
      response_time_minutes: form.response_time_minutes ? parseInt(form.response_time_minutes) : null,
      job_completed:         form.job_completed === 'yes' ? true : form.job_completed === 'no' ? false : null,
      would_recommend:       form.would_recommend === 'yes' ? true : form.would_recommend === 'no' ? false : null,
      review_text:           form.review_text,
      rating:                form.rating || null,
    }
    const res = await fetch(`${API}/api/reviews/questionnaire/${params.token}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    setSubmitting(false)
    if (res.ok) setStep('submitted')
    else {
      const d = await res.json()
      setErrorMsg(d.error ?? 'Something went wrong.')
      setStep('error')
    }
  }

  // ── Star rating ────────────────────────────────────────────────
  const StarRating = () => (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map(n => (
        <button key={n} type="button" onClick={() => setForm({ ...form, rating: n })}>
          <Star className={`w-7 h-7 transition-colors ${n <= form.rating
            ? 'fill-brand-amber text-brand-amber'
            : 'text-gray-300 hover:text-brand-amber'}`} />
        </button>
      ))}
    </div>
  )

  const Radio = ({ name, value, label }: { name: keyof typeof form; value: string; label: string }) => (
    <label className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border cursor-pointer text-sm transition-colors
      ${form[name] === value
        ? 'border-brand-green bg-brand-green-light text-brand-green font-medium'
        : 'border-brand-rule text-gray-600 hover:border-brand-green-mid'}`}>
      <input type="radio" name={name} value={value} className="sr-only"
        checked={form[name] === value}
        onChange={() => setForm({ ...form, [name]: value })} />
      {label}
    </label>
  )

  if (step === 'loading') return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-400 text-sm">Loading your review form…</p>
    </div>
  )

  if (step === 'error') return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-sm text-center">
        <div className="text-4xl mb-4">⚠️</div>
        <h1 className="font-serif text-2xl text-brand-ink mb-2">Oops</h1>
        <p className="text-gray-500 text-sm">{errorMsg}</p>
      </div>
    </div>
  )

  if (step === 'submitted') return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-brand-parchment">
      <div className="max-w-sm text-center">
        <CheckCircle className="w-14 h-14 text-brand-green mx-auto mb-4" />
        <h1 className="font-serif text-3xl text-brand-green mb-2">Thank you!</h1>
        <p className="text-gray-500 text-sm leading-relaxed">
          Your feedback helps Georgetown residents find reliable local providers.
          It will appear on the Georgetown Signal directory after a quick review.
        </p>
        <a href="/" className="gs-btn-primary inline-block mt-6">Back to Georgetown Signal</a>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-brand-parchment py-12 px-4">
      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <a href="/" className="font-serif text-xl text-brand-green">
            Georgetown<span className="text-brand-amber">Signal</span>
          </a>
          <h1 className="font-serif text-3xl text-brand-ink mt-4 mb-1">
            How did {bizName} do?
          </h1>
          <p className="text-gray-500 text-sm">
            Your honest feedback helps Georgetown residents find reliable {category.toLowerCase()} providers.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="gs-card space-y-6">

          {/* Star rating */}
          <div>
            <label className="gs-label">Overall rating</label>
            <StarRating />
          </div>

          {/* Response time */}
          <div>
            <label className="gs-label flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              How long did they take to first respond?
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                { label: 'Under 30 min', val: '20' },
                { label: '30–60 min',    val: '45' },
                { label: '1–2 hours',    val: '90' },
                { label: 'Half a day',   val: '240' },
                { label: 'Next day',     val: '1440' },
              ].map(o => (
                <Radio key={o.val} name="response_time_minutes" value={o.val} label={o.label} />
              ))}
            </div>
          </div>

          {/* Job completed */}
          <div>
            <label className="gs-label">Did they complete the job?</label>
            <div className="flex gap-3">
              <Radio name="job_completed" value="yes" label="Yes, fully" />
              <Radio name="job_completed" value="no"  label="No" />
            </div>
          </div>

          {/* Would recommend */}
          <div>
            <label className="gs-label">Would you recommend them to a neighbour?</label>
            <div className="flex gap-3">
              <Radio name="would_recommend" value="yes" label="Yes" />
              <Radio name="would_recommend" value="no"  label="No" />
            </div>
          </div>

          {/* Review text */}
          <div>
            <label className="gs-label">Tell Georgetown residents about your experience</label>
            <textarea
              rows={4}
              value={form.review_text}
              onChange={e => setForm({ ...form, review_text: e.target.value })}
              placeholder={`What was it like working with ${bizName}? Be specific — other residents will read this.`}
              className="gs-input resize-none"
            />
            <p className="text-xs text-gray-400 mt-1">
              Your review may be highlighted on the Georgetown Signal directory and news articles.
            </p>
          </div>

          <button type="submit" disabled={submitting || form.rating === 0}
            className="gs-btn-primary w-full py-3">
            {submitting ? 'Submitting…' : 'Submit review'}
          </button>

          <p className="text-xs text-gray-400 text-center">
            Reviews are analysed and approved before appearing publicly. No spam.
          </p>
        </form>
      </div>
    </div>
  )
}
