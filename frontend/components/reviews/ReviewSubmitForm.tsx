'use client'
import { useState } from 'react'
import { Star, CheckCircle } from 'lucide-react'

interface Props {
  businessSlug: string
  businessName: string
  businessId: number
}

export function ReviewSubmitForm({ businessId, businessName, businessSlug }: Props) {
  const [open,       setOpen]       = useState(false)
  const [submitted,  setSubmitted]  = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({ author_name: '', text: '', rating: 0 })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/reviews/submit/`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ business: businessId, ...form }),
    })
    setSubmitting(false)
    setSubmitted(true)
  }

  if (submitted) return (
    <div className="flex items-center gap-2 p-4 bg-brand-green-light rounded-xl text-brand-green text-sm">
      <CheckCircle className="w-5 h-5 flex-shrink-0" />
      <span>Thank you! Your review is being processed and will appear shortly.</span>
    </div>
  )

  if (!open) return (
    <button onClick={() => setOpen(true)}
      className="gs-btn-outline w-full text-sm py-3">
      + Leave a review for {businessName}
    </button>
  )

  return (
    <form onSubmit={handleSubmit} className="border border-brand-rule rounded-xl p-5 space-y-4 bg-white">
      <h3 className="font-serif text-lg text-brand-ink">Your review</h3>

      {/* Star rating */}
      <div>
        <label className="gs-label">Rating</label>
        <div className="flex gap-1">
          {[1,2,3,4,5].map(n => (
            <button key={n} type="button" onClick={() => setForm({ ...form, rating: n })}>
              <Star className={`w-6 h-6 transition-colors ${n <= form.rating
                ? 'fill-brand-amber text-brand-amber'
                : 'text-gray-300 hover:text-brand-amber'}`} />
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="gs-label">Your name</label>
        <input required type="text" value={form.author_name}
          onChange={e => setForm({ ...form, author_name: e.target.value })}
          placeholder="First name + last initial"
          className="gs-input" />
      </div>

      <div>
        <label className="gs-label">Your experience</label>
        <textarea required rows={3} value={form.text}
          onChange={e => setForm({ ...form, text: e.target.value })}
          placeholder={`Tell Georgetown residents about working with ${businessName}…`}
          className="gs-input resize-none" />
        <p className="text-xs text-gray-400 mt-1">
          Your review may be featured in Georgetown Signal news articles.
        </p>
      </div>

      <div className="flex gap-3">
        <button type="button" onClick={() => setOpen(false)}
          className="gs-btn-outline flex-1 text-sm py-2.5">Cancel</button>
        <button type="submit" disabled={submitting || form.rating === 0}
          className="gs-btn-primary flex-1 text-sm py-2.5">
          {submitting ? 'Submitting…' : 'Submit review'}
        </button>
      </div>
    </form>
  )
}
