'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ShieldCheck, Eye, EyeOff } from 'lucide-react'
import { createClient } from '@/lib/supabase'

export default function VendorSignupPage() {
  const router   = useRouter()
  const supabase = createClient()
  const [form, setForm]       = useState({ email: '', password: '', name: '' })
  const [showPw, setShowPw]   = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [done, setDone]       = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setError('')
    const { error } = await supabase.auth.signUp({
      email: form.email,
      password: form.password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
        data: { full_name: form.name },
      },
    })
    setLoading(false)
    if (error) setError(error.message)
    else setDone(true)
  }

  if (done) return (
    <div className="min-h-screen flex items-center justify-center bg-brand-parchment px-4">
      <div className="max-w-md w-full text-center">
        <ShieldCheck className="w-14 h-14 text-brand-green mx-auto mb-4" />
        <h1 className="font-serif text-3xl text-brand-green mb-2">Check your email</h1>
        <p className="text-gray-500 text-sm leading-relaxed">
          We sent a confirmation link to <strong>{form.email}</strong>.<br />
          Click it to activate your Georgetown Signal vendor account.
        </p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-parchment px-4 py-12">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="font-serif text-2xl text-brand-green">
            Georgetown<span className="text-brand-amber">Signal</span>
          </Link>
          <h1 className="font-serif text-3xl text-brand-ink mt-4 mb-1">List your business</h1>
          <p className="text-gray-500 text-sm">
            Join Georgetown's trusted local directory. Reach verified residents actively looking for your services.
          </p>
        </div>

        {/* Trust signals */}
        <div className="grid grid-cols-3 gap-3 mb-8">
          {[
            { num: '247', label: 'verified providers' },
            { num: '94%', label: 'resolution rate' },
            { num: '1.2k', label: 'signals / month' },
          ].map(s => (
            <div key={s.label} className="gs-card text-center py-3">
              <div className="font-serif text-2xl text-brand-green">{s.num}</div>
              <div className="text-xs text-gray-400 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="gs-card space-y-4">
          <div>
            <label className="gs-label">Your name</label>
            <input required type="text" value={form.name}
              onChange={e => setForm({...form, name: e.target.value})}
              placeholder="John Smith"
              className="gs-input" />
          </div>
          <div>
            <label className="gs-label">Email address</label>
            <input required type="email" value={form.email}
              onChange={e => setForm({...form, email: e.target.value})}
              placeholder="you@yourbusiness.com"
              className="gs-input" />
          </div>
          <div>
            <label className="gs-label">Password</label>
            <div className="relative">
              <input required type={showPw ? 'text' : 'password'} value={form.password}
                onChange={e => setForm({...form, password: e.target.value})}
                placeholder="Min 8 characters"
                className="gs-input pr-10" />
              <button type="button" onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button type="submit" disabled={loading} className="gs-btn-primary w-full py-3 text-center">
            {loading ? 'Creating account…' : 'Create vendor account — free'}
          </button>

          <p className="text-xs text-gray-400 text-center leading-relaxed">
            Your listing will be reviewed before going live. Signal Verified badge requires admin approval.
          </p>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-brand-green hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
